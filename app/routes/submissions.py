import pickle
from flask import Blueprint, jsonify, request
import pandas as pd
from app.models import db, Submissions
import numpy as np
import joblib

submissions_bp = Blueprint('submissions', __name__, url_prefix='/api/submissions')

model = 'models/best_model_approval.pkl'
with open(model, 'rb') as file:
    model = pickle.load(file)

@submissions_bp.route('/predict', methods=['POST'])
def predict():
    feature_input = request.get_json()

    total_children = float(feature_input['total_children'])
    total_income = float(feature_input['total_income'])
    total_family_members = float(feature_input['total_family_members'])
    applicant_age = float(feature_input['applicant_age'])
    years_of_working = float(feature_input['years_of_working'])
    total_bad_debt = float(feature_input['total_bad_debt'])
    total_good_debt = float(feature_input['total_good_debt'])

    income_type_commercial_associate = float(feature_input['income_type_commercial_associate'])
    income_type_pensioner = float(feature_input['income_type_pensioner'])
    income_type_state_servant = float(feature_input['income_type_state_servant'])
    income_type_student = float(feature_input['income_type_student'])
    income_type_working = float(feature_input['income_type_working'])

    family_status_married = float(feature_input['family_status_married'])
    family_status_separated = float(feature_input['family_status_separated'])
    family_status_single = float(feature_input['family_status_single'])
    family_status_widow = float(feature_input['family_status_widow'])

    housing_type_co_op_apartment = float(feature_input['housing_type_co_op_apartment'])
    housing_type_house_apartment = float(feature_input['housing_type_house_apartment'])
    housing_type_municipal_apartment = float(feature_input['housing_type_municipal_apartment'])
    housing_type_office_apartment = float(feature_input['housing_type_office_apartment'])
    housing_type_rented_apartment = float(feature_input['housing_type_rented_apartment'])
    housing_type_with_parents = float(feature_input['housing_type_with_parents'])

    # features = {
    #                 'total_children': total_children,
    #                 'total_income': total_income,
    #                 'income_type_commercial_associate': income_type_commercial,
    #                 'income_type_pensioner': income_type_pensioner,
    #                 'income_type_state_servant': income_type_state_servant,
    #                 'income_type_student': income_type_student,
    #                 'income_type_working': income_type_working,
    #                 'family_status_married': family_status_married,
    #                 'family_status_separated': family_status_separated,
    #                 'family_status_single': family_status_single,
    #                 'family_status_widow': family_status_widow,
    #                 'housing_type_co_op_apartment': housing_type_co_op_apartment,
    #                 'housing_type_house_apartment': housing_type_house,
    #                 'housing_type_municipal_apartment': housing_type_municipal,
    #                 'housing_type_office_apartment': housing_type_office,
    #                 'housing_type_rented_apartment': housing_type_rented,
    #                 'housing_type_with_parents': housing_type_with_parents
    #             } 
       
    
    features = [
        total_children,
        total_income,
        total_family_members,
        applicant_age,
        years_of_working,
        total_bad_debt,
        total_good_debt,

        income_type_commercial_associate,
        income_type_pensioner,
        income_type_state_servant,
        income_type_student,
        income_type_working,

        family_status_married,
        family_status_separated,
        family_status_single,
        family_status_widow,

        housing_type_co_op_apartment,
        housing_type_house_apartment,
        housing_type_municipal_apartment,
        housing_type_office_apartment,
        housing_type_rented_apartment,
        housing_type_with_parents
    ]

    
    # features_transform = np.log1p(features_df['total_income'])
    # prediction = model.predict({"Total_Children":0,"Total_Income":10.8197982842,"Income_Type_Commercial_Associate":1.0,"Income_Type_Pensioner":0.0,"Income_Type_State_Servant":0.0,"Income_Type_Student":0.0,"Income_Type_Working":0.0,"Family_Status_Civil_Marriage":1.0,"Family_Status_Married":1.0,"Family_Status_Separated":0.0,"Family_Status_Single_Or_Not_Married":0.0,"Family_Status_Widow":0.0,"Housing_Type_Co_op_Apartment":0.0,"Housing_Type_House_Or_Apartment":1.0,"Housing_Type_Municipal_Apartment":0.0,"Housing_Type_Office_Apartment":0.0,"Housing_Type_Rented_Apartment":0.0,"Housing_Type_With_Parents":0.0})
    prediction = model.predict([features])
    status_pengajuan = "DISETUJUI" if prediction[0] == 1 else "DITOLAK"

    result_predict = [{"status_pengajuan": status_pengajuan}]

    data = [feature_input] + result_predict
    merged = {**data[0], **data[1]}

    return jsonify(merged), 201