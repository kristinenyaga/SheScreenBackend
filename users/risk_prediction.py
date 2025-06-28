import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='sklearn')

class RiskPredictionData:
    def __init__(self, age, number_of_sexual_partners, first_sexual_intercourse, smoking_status, stds_history):
        self.age = age
        self.number_of_sexual_partners = number_of_sexual_partners
        self.first_sexual_intercourse = first_sexual_intercourse
        self.smoking_status = smoking_status
        self.stds_history = stds_history

# load model
model = joblib.load('models/cervical_cancer_kmeans_model.pkl')

# load pipelines
imputer = joblib.load("pipelines/cervical_cancer_imputer.pkl")
minmax_scaler = joblib.load("pipelines/cervical_cancer_minmax_scaler.pkl")
std_scaler = joblib.load("pipelines/cervical_cancer_std_scaler.pkl")


CLUSTER_INFO = {
    0: "Older, high sexual exposure, high STD risk",
    1: "Younger, moderate exposure, low risk",
    2: "Middle-aged, moderate exposure, high behavioral risk",
    3: "Middle-aged, moderate exposure, low risk",
    4: "Young, low exposure, some behavioral risk",
    5: "Older, long exposure, smokes, moderate risk"
}

# Screening recommendations based on cluster
SCREENING_RECOMMENDATIONS = {
    0: {
        "recommended_screenings": ["Pap Smear", "HPV DNA Test"],
        "reason": "High risk profile requires comprehensive cervical cancer screening to detect abnormal cells early",
        "urgency": "High",
        "frequency": "Annual screening recommended",
        "additional_services": []
    },
    1: {
        "recommended_screenings": ["HPV Vaccine"],
        "reason": "Young age with low risk - preventive vaccination is most effective",
        "urgency": "Medium", 
        "frequency": "Complete vaccination series as recommended",
        "additional_services": ["Sexual Education"]
    },
    2: {
        "recommended_screenings": ["Pap Smear", "HPV Vaccine"],
        "reason": "Moderate risk with behavioral factors requires both screening and prevention",
        "urgency": "High",
        "frequency": "Regular screening every 1-2 years",
        "additional_services": []
    },
    3: {
        "recommended_screenings": ["Pap Smear", "HPV Vaccine"],
        "reason": "Routine screening appropriate for age and risk profile",
        "urgency": "Medium",
        "frequency": "Regular screening every 2-3 years",
        "additional_services": []
    },
    4: {
        "recommended_screenings": ["HPV Vaccine"],
        "reason": "Young age ideal for preventive vaccination before exposure increases",
        "urgency": "Medium",
        "frequency": "Complete vaccination series as recommended", 
        "additional_services": ["Lifestyle Education", "Sexual Education"]
    },
    5: {
        "recommended_screenings": ["HPV Vaccine"],
        "reason": "Long exposure history with smoking risk factors - vaccination still beneficial",
        "urgency": "Medium",
        "frequency": "Complete vaccination series as recommended",
        "additional_services": ["Sexual Education", "Smoking Cessation Support"]
    }
}

def predict_risk(data):
    smoking_status_map = {
        "No": 0,
        "Yes": 1,
    }
    stds_map = {
        "No": 0,
        "Yes": 1,
    }
    smoking_status_num = smoking_status_map.get(data.smoking_status.strip().capitalize(), 0)
    stds_history_num = stds_map.get(data.stds_history.strip().capitalize(), 0)

    years_sexually_active = data.age - data.first_sexual_intercourse
    smokes_and_has_stds = smoking_status_num * stds_history_num
    sexual_partner_and_years_active = data.number_of_sexual_partners * years_sexually_active
    log_sexual_partners = np.log1p(data.number_of_sexual_partners)
    years_sexually_active_squared = years_sexually_active ** 2

    # Age group one-hot encoding
    age_group_25_35 = 0
    age_group_36_50 = 0
    age_group_50_plus = 0
    age_group_lt25 = 0
    if data.age < 25:
        age_group_lt25 = 1
    elif 25 <= data.age < 36:
        age_group_lt25 = 0
    elif 36 <= data.age <= 50:
        age_group_36_50 = 1
    elif data.age > 50:
        age_group_50_plus = 1

    # Risk score
    risk_score = (
        data.number_of_sexual_partners / 5 +
        (years_sexually_active / 30) +
        smoking_status_num +
        stds_history_num
    )

    risk_score = float(minmax_scaler.transform(np.array([[risk_score]]))[0][0])

    # Prepare input features
    X = np.array([[
        smoking_status_num,        
        stds_history_num, 
        risk_score,
        smokes_and_has_stds,
        sexual_partner_and_years_active,
        log_sexual_partners,
        years_sexually_active_squared,
        age_group_25_35,
        age_group_36_50,
        age_group_50_plus,
        age_group_lt25
    ]])

    X_scaled = std_scaler.transform(X)

    X_imputed = imputer.transform(X_scaled)

    cluster = int(model.predict(X_imputed)[0])
    interpretation = CLUSTER_INFO.get(cluster, "Unknown cluster")
    screening_recommendations = SCREENING_RECOMMENDATIONS.get(cluster, {})
    
    return {
        "cluster": cluster,
        "interpretation": interpretation,
        "screening_recommendations": screening_recommendations
    }