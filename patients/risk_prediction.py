import joblib
import numpy as np
import pandas as pd
import pickle
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

class RiskPredictionData:
    def __init__(self, age, number_of_sexual_partners, first_sexual_intercourse, smoking_status, stds_history, hpv_test_result, hpv_vaccinated=False):
        self.age = age
        self.number_of_sexual_partners = number_of_sexual_partners
        self.first_sexual_intercourse = first_sexual_intercourse
        self.smoking_status = smoking_status
        self.stds_history = stds_history
        self.hpv_test_result = hpv_test_result
        self.hpv_vaccinated = hpv_vaccinated


kmeans_selected = None
selector = None
full_risk_pipeline = None

# Load models and pipelines
kmeans_selected = joblib.load("models/cervical_cancer_kmeans_selected_model.pkl")
selector = joblib.load("pipelines/cervical_cancer_feature_selector.pkl")
full_risk_pipeline = joblib.load("pipelines/cervical_cancer_risk_pipeline.pkl")

# Load selected feature names
with open('selected_feature_names.pkl', 'rb') as f:
    selected_feature_names = pickle.load(f)

selected_feature_names = []

# Probability thresholds
def get_risk_category(risk_probability, hpv_positive):
    if hpv_positive == 1:
        return "High Risk", "HPV Positive - Immediate screening required"
    elif risk_probability < 0.3:
        return "Low Risk", "Minimal risk factors - Regular screening recommended"
    elif risk_probability < 0.6:
        return "Moderate Risk", "Some risk factors present - Consider more frequent screening"
    else:
        return "High Risk", "Multiple risk factors - Immediate screening recommended"

def get_detailed_recommendation(risk_probability, hpv_positive, age, hpv_vaccinated=False):
    base_recommendations = []
    additional_services = []
    
    if age >= 25:
        base_recommendations.append("Pap Smear")
    
    if hpv_positive == 1:
        base_recommendations.extend(["HPV DNA Test"])
        if "Pap Smear" not in base_recommendations:
            base_recommendations.append("Pap Smear")
            
        return {
            "immediate_action": "HPV DNA testing and Pap smear",
            "recommended_screenings": base_recommendations,
            "reason": "HPV positive status requires immediate specialized care",
        }
    
    elif risk_probability < 0.3:
        if age < 25:
            base_recommendations.append("HPV Vaccine")
            additional_services.append("Sexual Education")
            return {
                "immediate_action": "Continue regular preventive care and get HPV vaccine",
                "recommended_screenings": base_recommendations,
                "reason": "Young age with low risk - preventive vaccination is most effective",
                "urgency": "Low",
                "additional_services": additional_services
            }
        else:
            if not hpv_vaccinated and age >= 25:
                base_recommendations.append("HPV Vaccine")
                additional_services.append("HPV Vaccine Education")
                
            return {
                "immediate_action": "Schedule routine Pap smear" + (" and consider HPV vaccine" if "HPV Vaccine" in base_recommendations else ""),
                "recommended_screenings": base_recommendations,
                "reason": "Low risk - routine screening appropriate" + (" with HPV vaccine for additional protection" if "HPV Vaccine" in base_recommendations else ""),
                "urgency": "Low",
                "additional_services": additional_services
            }
    
    elif risk_probability < 0.6:
        base_recommendations.append("HPV DNA Test")
        additional_services.append("Risk Factor Counseling")
        
        return {
            "immediate_action": "Schedule Pap smear and HPV testing",
            "recommended_screenings": base_recommendations,
            "reason": "Moderate risk factors present - more frequent screening recommended",
            "urgency": "Medium",
            "additional_services": additional_services
        }
    
    else:
        base_recommendations.append("HPV DNA Test")
        additional_services.extend(["Risk Factor Counseling", "Lifestyle Education"])
        
        return {
            "immediate_action": "Schedule immediate screening - Pap smear and HPV testing",
            "recommended_screenings": base_recommendations,
            "reason": "High risk factors present - immediate comprehensive screening required",
            "urgency": "High",
            "additional_services": additional_services
        }

def predict_risk(data):
    smoking_status_map = {
        "No": 0, "N": 0,
        "Yes": 1, "Y": 1,
    }
    stds_map = {
        "No": 0, "N": 0,
        "Yes": 1, "Y": 1,
    }
    hpv_map = {
        "NEGATIVE": 0, "N": 0, "NO": 0,
        "POSITIVE": 1, "Y": 1, "YES": 1, "UNKNOWN": 0
    }
    
    smoking_status_num = smoking_status_map.get(data.smoking_status.strip().upper(), 0)
    stds_history_num = stds_map.get(data.stds_history.strip().upper(), 0)
    hpv_results_num = hpv_map.get(data.hpv_test_result.strip().upper(), 0)

    # Feature engineered features
    years_sexually_active = data.age - data.first_sexual_intercourse
    smokes_and_has_stds = smoking_status_num * stds_history_num
    sexual_partner_and_years_active = data.number_of_sexual_partners * years_sexually_active
    log_sexual_partners = np.log1p(data.number_of_sexual_partners)
    years_sexually_active_squared = years_sexually_active ** 2
    
    # HPV engineered features
    hpv_and_stds = hpv_results_num * stds_history_num
    hpv_and_smoking = hpv_results_num * smoking_status_num
    high_risk_score = 1 if (data.number_of_sexual_partners / 5 + years_sexually_active / 30 + smoking_status_num + stds_history_num) > 2.5 else 0
    early_sexual_activity = 1 if data.first_sexual_intercourse < 18 else 0

    # Risk score
    risk_score = (
        data.number_of_sexual_partners / 5 +
        (years_sexually_active / 30) +
        smoking_status_num +
        stds_history_num
    )

    # Age group
    if data.age < 25:
        age_group = '<25'
    elif 25 <= data.age < 36:
        age_group = '25-35'
    elif 36 <= data.age <= 50:
        age_group = '36-50'
    else:
        age_group = '50+'

    input_data = pd.DataFrame({
        'Age': [data.age],
        'Sexual Partners': [data.number_of_sexual_partners],
        'First Sexual Activity Age': [data.first_sexual_intercourse],
        'Smoking Status': [data.smoking_status],
        'STDs History': [data.stds_history],
        'HPV Test Result': [data.hpv_test_result],
        'Years_Sexually_Active': [years_sexually_active],
        'Smoking_Status_Num': [smoking_status_num],
        'STDs_History_Num': [stds_history_num],
        'HPV_Test_Result_Num': [hpv_results_num],
        'Risk_Score': [risk_score],
        'Smokes_and_Has_STDs': [smokes_and_has_stds],
        'Sexual_Partner_and_Years_Active': [sexual_partner_and_years_active],
        'Log_Sexual_Partners': [log_sexual_partners],
        'Years_Sexually_Active_Squared': [years_sexually_active_squared],
        'HPV_and_STDs': [hpv_and_stds],
        'HPV_and_Smoking': [hpv_and_smoking],
        'High_Risk_Score': [high_risk_score],
        'Early_Sexual_Activity': [early_sexual_activity],
        'Age_Group': [age_group]
    })

    X_transformed = full_risk_pipeline.transform(input_data)
    X_selected = selector.transform(X_transformed)
    cluster = int(kmeans_selected.predict(X_selected)[0])

        # Calculate risk probability
    cluster_centers = kmeans_selected.cluster_centers_
    distances = np.linalg.norm(X_selected - cluster_centers, axis=1)
    risk_probability = float(distances[cluster] / np.max(distances))

    risk_category, risk_description = get_risk_category(
        risk_probability, hpv_results_num)
    detailed_recommendation = get_detailed_recommendation(
        risk_probability, hpv_results_num, data.age, data.hpv_vaccinated)

    return {
        "interpretation": f"Risk Category: {risk_category} - {risk_description}",
        "risk_probability": risk_probability,
        "risk_category": risk_category,
        "risk_description": risk_description,
        "screening_recommendations": detailed_recommendation,
        "risk_factors": {
            "hpv_positive": hpv_results_num == 1,
            "smoking": smoking_status_num == 1,
            "stds_history": stds_history_num == 1,
            "early_sexual_activity": early_sexual_activity == 1,
            "multiple_partners": data.number_of_sexual_partners > 2,
            "age_group": age_group
        },
        "selected_features": selected_feature_names
        }

