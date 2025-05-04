from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.models import Submissions
from app.database import get_db
from app.services.jwt import token_required
import joblib
import numpy as np
import pandas as pd
import pdfplumber as pr
import re
import xgboost as xgb

CATEGORY_MODEL_PATH = 'models/best_model_credit.json'
CATEGORY_SCALER_PATH = 'models/scaler_credit.pkl'

category_model = xgb.Booster()
category_model.load_model(CATEGORY_MODEL_PATH)
category_scaler = joblib.load(CATEGORY_SCALER_PATH)

COLUMNS = [
    'total_children',
    'total_income',
    'applicant_age',
    'years_of_working',
    'total_bad_debt',
    'total_good_debt',
    'income_type_commercial_associate',
    'income_type_pensioner',
    'income_type_state_servant',
    'income_type_student',
    'income_type_working',
    'family_status_married',
    'family_status_separated',
    'family_status_single',
    'family_status_widow',
    'housing_type_co_op_apartment',
    'housing_type_house_apartment',
    'housing_type_municipal_apartment',
    'housing_type_office_apartment',
    'housing_type_rented_apartment',
    'housing_type_with_parents',
]

CAT_FEATURES = list(category_scaler.feature_names_in_)

router = APIRouter(
    prefix="/api/submissions",
    tags=["submissions"]
)

@router.get("/")
def get_submissions(user_id: int = Depends(token_required), db: Session = Depends(get_db)):
    submission = db.query(Submissions).filter_by(user_id=user_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission tidak ditemukan")
    return submission.to_dict()

@router.post("/read_pdf", status_code=201)
def read_Pdf(file: UploadFile = File(...)):
    with pr.open(file.file) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        table = tables[0]

        header = table[0]
        target_column = None

        def clean_to_int(s):
            return int(re.sub(r'[^0-9]', '', s))

        for idx, col_name in enumerate(header):
            if 'PENGHASILAN BRUTO' in (col_name or '').upper():
                target_column = idx
                break

        if target_column is not None:
            bruto_values = [row[target_column] for row in table[1:] if row[target_column]]
            gaji = clean_to_int(bruto_values[1])
            total_income = gaji * 12
            return total_income
        else:
            raise ValueError("Kolom Jumlah Penghasilan Bruto tidak ditemukan.")

def extract_total_income_from_pdf(file):
    with pr.open(file) as pdf:
        page = pdf.pages[0]
        tables = page.extract_tables()
        table = tables[0]

        header = table[0]
        target_column = None

        def clean_to_int(s):
            return int(re.sub(r'[^0-9]', '', s))

        for idx, col_name in enumerate(header):
            if 'PENGHASILAN BRUTO' in (col_name or '').upper():
                target_column = idx
                break

        if target_column is not None:
            bruto_values = [row[target_column] for row in table[1:] if row[target_column]]
            gaji = clean_to_int(bruto_values[1])
            total_income = gaji * 12
            return total_income
        else:
            raise ValueError("Kolom Jumlah Penghasilan Bruto tidak ditemukan.")

def build_input_df(data):
    """
    Validate input, apply log-transform, and return DataFrame of raw features.
    """
    values = {}
    for col in COLUMNS:
        if col not in data:
            raise KeyError(col)
        try:
            values[col] = float(data[col])
        except ValueError:
            raise ValueError(f"Invalid numeric value for {col}")

    for col in ['total_income', 'total_bad_debt', 'years_of_working']:
        values[col] = np.log(values[col] + 1)

    return pd.DataFrame([values], columns=COLUMNS)

def apply_business_rules(original_data, predicted_class):
    """
    Apply business rules to override model predictions using the original data
    before transformations and scaling
    
    Args:
        original_data: DataFrame containing the original application data
        predicted_class: The model's predicted class
    
    Returns:
        final_class: The final decision after applying business rules
        reason: Reason for disapproval if applicable
    """
    # Default is to trust the model's prediction
    final_class = predicted_class
    reason = None
    
    # Access the original values (before log transform and scaling)
    total_income = original_data['total_income'].iloc[0]
    total_bad_debt = original_data['total_bad_debt'].iloc[0]
    years_working = original_data['years_of_working'].iloc[0]
    applicant_age = original_data['applicant_age'].iloc[0]
    is_student = original_data['income_type_student'].iloc[0] == 1
    total_good_debt = original_data['total_good_debt'].iloc[0]
    
    min_income = 36000000

    # Rule 1: Student with no income and no credit history
    if is_student and total_income <= min_income and years_working == 0:
        final_class = 0 
        reason = "Pengajuan ditolak karena status pelajar dan tidak memiliki penghasilan yang cukup"
    
    # Rule 2: Applicant with high bad debt ratio
    if total_bad_debt > 0:
        bad_debt_ratio = total_bad_debt / (total_income + 1)
        if bad_debt_ratio > 0.5:
            final_class = 0
            reason = "Pengajuan ditolak karena rasio utang buruk terlalu tinggi"
    
    # Rule 3: Age limit
    if applicant_age < 21:
        final_class = 0
        reason = "Pengajuan ditolak karena usia di bawah 21 tahun"
    
    # Rule 4: Income requirement
    if total_income < min_income:
        final_class = 0
        reason = f"Gaji total di bawah standar minimum yaitu Rp 36.000.000 per tahun atau Rp 3.000.000 per bulan"
    
    return final_class, reason

@router.post("/predict", status_code=201)
def predict(
    user_id: int = Depends(token_required),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="Tidak ada berkas yang dipilih")

    try:
        total_income = extract_total_income_from_pdf(file.file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal ekstrak pendapatan dari PDF: {str(e)}")

    submission = db.query(Submissions).filter_by(user_id=user_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Data pengajuan tidak ditemukan")
    
    payload = {
        "total_children": submission.total_children,
        "total_income": total_income,
        "applicant_age": submission.applicant_age,
        "years_of_working": submission.years_of_working,
        "total_bad_debt": submission.total_bad_debt,
        "total_good_debt": submission.total_good_debt,

        "income_type_commercial_associate": int(submission.income_type == "Commercial Associate"),
        "income_type_pensioner": int(submission.income_type == "Pensioner"),
        "income_type_state_servant": int(submission.income_type == "State Servant"),
        "income_type_student": int(submission.income_type == "Student"),
        "income_type_working": int(submission.income_type == "Working"),

        "family_status_married": int(submission.family_status == "Married"),
        "family_status_separated": int(submission.family_status == "Separated"),
        "family_status_single": int(submission.family_status == "Single"),
        "family_status_widow": int(submission.family_status == "Widow"),

        "housing_type_co_op_apartment": int(submission.house_category == "Co-op Apartment"),
        "housing_type_house_apartment": int(submission.house_category == "House Apartment"),
        "housing_type_municipal_apartment": int(submission.house_category == "Municipal Apartment"),
        "housing_type_office_apartment": int(submission.house_category == "Office Apartment"),
        "housing_type_rented_apartment": int(submission.house_category == "Rented Apartment"),
        "housing_type_with_parents": int(submission.house_category == "With Parents"),
    }

    try:
        # Store the original data (before transforms)
        original_data = pd.DataFrame([payload])
        # Process data as before
        raw_df = build_input_df(payload)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e.args[0]}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Scale + predict approval
    X_scaled = category_scaler.transform(raw_df)
    dtest = xgb.DMatrix(X_scaled, feature_names=COLUMNS)
    
    # Get model prediction
    pred_probabilities = category_model.predict(dtest)[0]
    predicted_class = int(np.argmax(pred_probabilities))
    
    # Apply business rules using original data
    final_class, rejection_reason = apply_business_rules(original_data, predicted_class)
    
    # Prepare response
    result = payload.copy()
    result['limit_category'] = int(final_class)
    # result['model_confidence'] = float(pred_probabilities[predicted_class])

    # submission.status_pengajuan = final_class
    
    # Add additional info if rejected due to business rules
    if rejection_reason:
        result['rejection_reason'] = rejection_reason
        submission.status_pengajuan=rejection_reason
    else:
        result['rejection_reason'] = ""
        submission.status_pengajuan=""
    
    submission.total_income = total_income
    submission.tnc = True
    submission.file_bpp = file.filename
    
    db.commit()

    return result

# APPROVAL_MODEL_PATH = 'models/best_model_approval.pkl'
# APPROVAL_SCALER_PATH = 'models/scaler_approval.pkl'
# CATEGORY_MODEL_PATH = 'models/best_model_credit.pkl'
# CATEGORY_SCALER_PATH = 'models/scaler_credit.pkl'

# approval_model = joblib.load(APPROVAL_MODEL_PATH)
# approval_scaler = joblib.load(APPROVAL_SCALER_PATH)
# category_model = joblib.load(CATEGORY_MODEL_PATH)
# category_scaler = joblib.load(CATEGORY_SCALER_PATH)

# COLUMNS = [
#     'total_children', 'total_income', 'applicant_age', 'years_of_working',
#     'total_bad_debt', 'total_good_debt', 'income_type_commercial_associate',
#     'income_type_pensioner', 'income_type_state_servant', 'income_type_student',
#     'income_type_working', 'family_status_married', 'family_status_separated',
#     'family_status_single', 'family_status_widow', 'housing_type_co_op_apartment',
#     'housing_type_house_apartment', 'housing_type_municipal_apartment',
#     'housing_type_office_apartment', 'housing_type_rented_apartment',
#     'housing_type_with_parents'
# ]
# CAT_FEATURES = list(category_scaler.feature_names_in_)

# def build_input_df(data):
#     """
#     Validate input, apply log-transform, and return DataFrame of raw features.
#     """
#     values = {}
#     for col in COLUMNS:
#         if col not in data:
#             raise KeyError(col)
#         try:
#             values[col] = float(data[col])
#         except ValueError:
#             raise ValueError(f"Invalid numeric value for {col}")

#     for col in ['years_of_working', 'total_bad_debt']:
#         values[col] = np.log(values[col] + 1)

#     return pd.DataFrame([values], columns=COLUMNS)

# @router.post("/predict_category", status_code=201)
# def predict_category(
#     user_id: int = Depends(token_required),
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     if not file or not file.filename:
#         raise HTTPException(status_code=400, detail="Tidak ada berkas yang dipilih")

#     try:
#         total_income = extract_total_income_from_pdf(file.file)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Gagal ekstrak pendapatan dari PDF: {str(e)}")

#     submission = db.query(Submissions).filter_by(user_id=user_id).first()
#     if not submission:
#         raise HTTPException(status_code=404, detail="Data pengajuan tidak ditemukan")

#     payload = {
#         "total_children": submission.total_children,
#         "total_income": total_income,
#         "applicant_age": submission.applicant_age,
#         "years_of_working": submission.years_of_working,
#         "total_bad_debt": submission.total_bad_debt,
#         "total_good_debt": submission.total_good_debt,

#         "income_type_commercial_associate": int(submission.income_type == "Commercial Associate"),
#         "income_type_pensioner": int(submission.income_type == "Pensioner"),
#         "income_type_state_servant": int(submission.income_type == "State Servant"),
#         "income_type_student": int(submission.income_type == "Student"),
#         "income_type_working": int(submission.income_type == "Working"),

#         "family_status_married": int(submission.family_status == "Married"),
#         "family_status_separated": int(submission.family_status == "Separated"),
#         "family_status_single": int(submission.family_status == "Single"),
#         "family_status_widow": int(submission.family_status == "Widow"),

#         "housing_type_co_op_apartment": int(submission.house_category == "Co-op Apartment"),
#         "housing_type_house_apartment": int(submission.house_category == "House Apartment"),
#         "housing_type_municipal_apartment": int(submission.house_category == "Municipal Apartment"),
#         "housing_type_office_apartment": int(submission.house_category == "Office Apartment"),
#         "housing_type_rented_apartment": int(submission.house_category == "Rented Apartment"),
#         "housing_type_with_parents": int(submission.house_category == "With Parents"),
#     }

#     try:
#         raw_df = build_input_df(payload)
#     except (KeyError, ValueError) as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     X_app = approval_scaler.transform(raw_df)
#     app_pred = approval_model.predict(X_app)[0]
#     status_num = int(app_pred)
#     status = 'DISETUJUI' if status_num == 1 else 'DITOLAK'

#     cat_df = raw_df.copy()
#     cat_df['status'] = status_num
#     cat_df = cat_df[CAT_FEATURES]

#     X_cat_scaled = category_scaler.transform(cat_df)
#     cat_pred = category_model.predict(X_cat_scaled)[0]

#     result = payload.copy()
#     result['status_pengajuan'] = status
#     result['credit_card_category'] = int(cat_pred)

#     submission.status_pengajuan = status
#     submission.total_income = total_income
#     submission.tnc = True
#     submission.file_bpp = file.filename
#     db.commit()

#     return result