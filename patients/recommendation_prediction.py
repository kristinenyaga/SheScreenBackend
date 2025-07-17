import numpy as np
import pandas as pd
import warnings
import joblib

warnings.filterwarnings("ignore", category=FutureWarning)

# Load recommendation model
try:
    recommendation_model = joblib.load("models/cervical_cancer_rf_model.pkl")
    recommendation_pipeline = joblib.load("pipelines/cervical_cancer_full_pipeline.pkl")
    print("Recommendation model loaded successfully")
except Exception as e:
    print(f"Error loading recommendation model: {e}")
    recommendation_model = None
    recommendation_pipeline = None

class RecommendationPredictionData:
    def __init__(self, age: int, number_of_sexual_partners: int, first_sexual_intercourse: int,
                 smoking_status: str, stds_history: str, hpv_current_test_result: str,
                 pap_smear_result: str, screening_type_last: str):
        self.age = age
        self.number_of_sexual_partners = number_of_sexual_partners
        self.first_sexual_intercourse = first_sexual_intercourse    
        self.smoking_status = smoking_status
        self.stds_history = stds_history
        self.hpv_current_test_result = hpv_current_test_result
        self.pap_smear_result = pap_smear_result
        self.screening_type_last = screening_type_last

def get_detailed_recommendations(prediction_label: int, hpv_result: str, pap_result: str):
    recommendations = {
        0: {  # Follow-up Screening
            "category": "Follow-up Screening",
            "options": [
                "REPEAT PAP SMEAR IN 3 YEARS",
                "FOR PAP SMEAR",
                "FOR HPV VACCINE AND SEXUAL EDUCATION"
            ]
        },
        1: {  # General Follow-up
            "category": "General Follow-up", 
            "options": [
                "FOR ANNUAL FOLLOW UP AND PAP SMEAR IN 3 YEARS",
                "REPEAT PAP SMEAR IN 3 YEARS AND FOR HPV VACCINE"
            ]
        },
        2: {  # Diagnostic evaluation and treatment
            "category": "Diagnostic evaluation and treatment",
            "options": [
                "FOR COLPOSCOPY BIOPSY",
                "CYTOLOGY",
                "FOR COLPOSCOPY BIOPSY AND CYTOLOGY+/- TAH",
                "FOR BIOPSY AND CYTOLOGY WITH TAH NOT RECOMMENDED",
                "FOR LASER THERAPY",
                "FOR COLPOSCOPY, CYTOLOGY THEN LASER THERAPY",
                "FOR COLPOSCOPY BIOPSY, CYTOLOGY +/- TAH"
            ]
        }
    }
    
    base_recommendation = recommendations.get(prediction_label, {
        "category": "Unknown",
        "options": ["Consult Healthcare Provider"]
    })
    
    context = []
    if hpv_result.upper() == "POSITIVE":
        context.append("HPV positive result requires immediate attention")
    if pap_result.upper() == "POSITIVE":
        context.append(f"Pap smear shows {pap_result} - follow recommended protocol")
    
    return {
        "category": base_recommendation["category"],
        "options": base_recommendation["options"],
        "context": context,
        "prediction_label": prediction_label
    }

def get_recommendation(prediction_data: RecommendationPredictionData):

    try:
        if recommendation_model is not None and recommendation_pipeline is not None:
            smoking_status_map = {"No": 0, "Yes": 1, "N": 0, "Y": 1}
            stds_map = {"No": 0, "Yes": 1, "N": 0, "Y": 1}
            pap_smear_map = {'N': 0, 'Y': 1, 'NEGATIVE': 0, 'POSITIVE': 1}
            hpv_map = {'NEGATIVE': 0, 'POSITIVE': 1, 'N': 0, 'Y': 1}
            
            smoking_status_num = smoking_status_map.get(prediction_data.smoking_status.strip().capitalize(), 0)
            stds_history_num = stds_map.get(prediction_data.stds_history.strip().capitalize(), 0)
            hpv_results_num = hpv_map.get(prediction_data.hpv_current_test_result.strip().upper(), 0)
            pap_smear_results_num = pap_smear_map.get(prediction_data.pap_smear_result.strip().upper(), 0)

            years_sexually_active = prediction_data.age - prediction_data.first_sexual_intercourse
            smokes_and_has_stds = smoking_status_num * stds_history_num
            sexual_partner_and_years_active = prediction_data.number_of_sexual_partners * years_sexually_active
            log_sexual_partners = np.log1p(prediction_data.number_of_sexual_partners)
            years_sexually_active_squared = years_sexually_active ** 2

            risk_score = (
                prediction_data.number_of_sexual_partners / 5 +
                (years_sexually_active / 30) +
                smoking_status_num +
                stds_history_num
            )

            if prediction_data.age < 25:
                age_group = '<25'
            elif prediction_data.age < 35:
                age_group = '25-35'
            elif prediction_data.age < 50:
                age_group = '36-50'
            else:
                age_group = '50+'

            feature_data = {
                'Smoking_Status_Num': [smoking_status_num],
                'STDs_History_Num': [stds_history_num], 
                'Years_Sexually_Active': [years_sexually_active],
                'Smokes_and_Has_STDs': [smokes_and_has_stds],
                'Sexual_Partner_and_Years_Active': [sexual_partner_and_years_active],
                'Risk_Score': [risk_score],
                'Log_Sexual_Partners': [log_sexual_partners],
                'Years_Sexually_Active_Squared': [years_sexually_active_squared],
                'Pap_Smear_Result_Num': [pap_smear_results_num],
                'HPV_Test_Result_Num': [hpv_results_num],
                'Age_Group': [age_group],
                'Screening Type Last': [prediction_data.screening_type_last.strip().upper()]
            }

            X_df = pd.DataFrame(feature_data)
            X_transformed = recommendation_pipeline.transform(X_df)
            prediction_proba = recommendation_model.predict_proba(X_transformed)
            prediction_label = int(np.argmax(prediction_proba[0]))
            
            detailed_recommendations = get_detailed_recommendations(
                prediction_label, 
                prediction_data.hpv_current_test_result, 
                prediction_data.pap_smear_result
            )
            
            return {
                **detailed_recommendations,
                "prediction_probabilities": prediction_proba[0].tolist(),
                "confidence": float(np.max(prediction_proba[0]))
            }
            
    except Exception as e:
        print(f"ML model failed, using clinical rules: {e}")
        pass
    
    hpv_positive = prediction_data.hpv_current_test_result.lower() == "positive"
    pap_positive = prediction_data.pap_smear_result.lower() == "positive"
    
    if hpv_positive and pap_positive:
        prediction_label = 2  
    elif hpv_positive or pap_positive:
        prediction_label = 1  
    else:
        prediction_label = 0
    
    detailed_recommendations = get_detailed_recommendations(
        prediction_label, 
        prediction_data.hpv_current_test_result, 
        prediction_data.pap_smear_result
    )
    
    return {
        **detailed_recommendations,
        "confidence": 0.85, 
        "method": "clinical_rules"
    }
   


