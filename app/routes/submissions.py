import joblib
from flask import Blueprint, jsonify, request
import numpy as np
import pandas as pd

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
def predict():
    payload = request.get_json() or {}
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

    result = payload.copy()
    result['status_pengajuan'] = status
    return jsonify(result), 201


@submissions_bp.route('/predict_category', methods=['POST'])
def predict_category():
    payload = request.get_json() or {}
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
    return jsonify(result), 201
