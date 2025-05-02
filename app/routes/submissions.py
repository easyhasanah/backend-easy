import joblib
from flask import Blueprint, jsonify, request
import numpy as np
import pandas as pd
from app.models import db, Submissions
from app.services.jwt import token_required
import pdfplumber as pr
import re

submissions_bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')

# Paths to saved artifacts
APPROVAL_MODEL_PATH = 'models/best_model_approval.pkl'
APPROVAL_SCALER_PATH = 'models/scaler_approval.pkl'
CATEGORY_MODEL_PATH = 'models/best_model_credit.pkl'
CATEGORY_SCALER_PATH = 'models/scaler_credit.pkl'

# Load artifacts
approval_model = joblib.load(APPROVAL_MODEL_PATH)
approval_scaler = joblib.load(APPROVAL_SCALER_PATH)
category_model = joblib.load(CATEGORY_MODEL_PATH)
category_scaler = joblib.load(CATEGORY_SCALER_PATH)

# Feature columns for raw input
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
# Derive expected column order for category scaler
CAT_FEATURES = list(category_scaler.feature_names_in_)


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

    # Log-transform numeric skewed features
    for col in ['years_of_working', 'total_bad_debt']:
        values[col] = np.log(values[col] + 1)

    return pd.DataFrame([values], columns=COLUMNS)


@submissions_bp.route('/predict', methods=['POST'])
@token_required
def predict(user_id):
    submission = Submissions.query.filter_by(user_id=user_id).first_or_404()
    payload = {
        "total_children": submission.total_children,
        "total_income": submission.income,
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
        raw_df = build_input_df(payload)
    except KeyError as e:
        return jsonify({'error': f"Missing field: {e.args[0]}"}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Scale + predict approval
    X_scaled = approval_scaler.transform(raw_df)
    pred = approval_model.predict(X_scaled)[0]
    status = 'DISETUJUI' if pred == 1 else 'DITOLAK'

    submission.status_pengajuan = status
    db.session.commit()

    result = payload.copy()
    result['status_pengajuan'] = status
    return jsonify(result), 201


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

@submissions_bp.route('/predict_category', methods=['POST'])
@token_required
def predict_category(user_id):
    file = request.files['file']

    try:
        total_income = extract_total_income_from_pdf(file)
    except Exception as e:
        return jsonify({'error': f"Failed to extract income from PDF: {str(e)}"}), 500

    # payload = request.get_json() or {}
    submission = Submissions.query.filter_by(user_id=user_id).first_or_404()
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
        raw_df = build_input_df(payload)
    except KeyError as e:
        return jsonify({'error': f"Missing field: {e.args[0]}"}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Step 1: approval
    X_app = approval_scaler.transform(raw_df)
    app_pred = approval_model.predict(X_app)[0]
    status_num = int(app_pred)
    status = 'DISETUJUI' if app_pred == 1 else 'DITOLAK'

    # Step 2: prepare features for category (include status)
    cat_df = raw_df.copy()
    cat_df['status'] = status_num
    # Reorder to match scaler's expected feature names exactly
    cat_df = cat_df[CAT_FEATURES]

    # Scale + predict category
    X_cat_scaled = category_scaler.transform(cat_df)
    cat_pred = category_model.predict(X_cat_scaled)[0]

    result = payload.copy()
    result['status_pengajuan'] = status
    result['credit_card_category'] = int(cat_pred)

    submission.status_pengajuan = status
    submission.income = total_income
    db.session.commit()

    return jsonify(result), 201

@submissions_bp.route('/', methods=['GET'])
@token_required
def get_submissions(user_id):
    submission = Submissions.query.filter_by(user_id=user_id).first_or_404()
    return jsonify(submission.to_dict())