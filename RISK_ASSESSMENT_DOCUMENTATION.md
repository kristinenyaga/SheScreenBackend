# Cervical Cancer Risk Assessment System


## Features

### 1. HPV Testing Integration
- **HPV Test Result Field**: Added `hpv_test_result` field to risk assessments
- **Risk Calculation**: HPV status significantly impacts risk categorization
- **Immediate Action**: HPV-positive results trigger immediate screening recommendations

### 2. HPV Vaccination Tracking
- **Vaccination Status Field**: Added `hpv_vaccinated` field to track vaccination history
- **Age-Based Vaccine Recommendations**: Adults >25 with low risk and no prior vaccination receive vaccine recommendations
- **3-Dose Schedule**: Unvaccinated low-risk adults receive HPV vaccine recommendations

### 3. Age-Based Clinical Guidelines
- **Mandatory Pap Smears at 25+**: All patients ≥25 years receive Pap smear recommendations regardless of risk level
- **HPV Vaccine for Adults**: Unvaccinated adults >25 with low risk receive vaccine recommendations
- **Age-Specific Screening**: Different screening schedules based on age groups

### 4. Enhanced Risk Categories
- **Low Risk** (< 0.3): Minimal risk factors - Regular screening recommended
- **Moderate Risk** (0.3 - 0.6): Some risk factors present - More frequent screening
- **High Risk** (> 0.6): Multiple risk factors - Immediate screening required
- **HPV Positive**: Immediate specialized care required regardless of other factors

### 3. Detailed Recommendations
Each risk assessment now provides:
- **Immediate Action**: What to do right away
- **Follow-up**: Next steps and ongoing care
- **Screening Frequency**: How often to get screened
- **Recommended Screenings**: Specific tests (Pap Smear, HPV DNA Test, HPV Vaccine)
- **Additional Services**: Support services (counseling, education, etc.)

## API responses

### Risk Assessment Request
```json
{
  "number_of_sexual_partners": 2,
  "first_sexual_intercourse_age": 18,
  "smoking_status": "No",
  "stds_history": "No",
  "hpv_test_result": "Negative",
  "hpv_vaccinated": false
}
```

### Enhanced Response
```json
{
  "cluster": 1,
  "interpretation": "Risk Category: Low Risk - Minimal risk factors present",
  "risk_probability": 0.25,
  "risk_category": "Low Risk",
  "screening_recommendations": {
    "immediate_action": "Schedule routine Pap smear",
    "follow_up": "Maintain regular screening schedule",
    "screening_frequency": "Every 3 years with Pap smear",
    "recommended_screenings": ["Pap Smear"],
    "reason": "Low risk - routine screening appropriate",
    "urgency": "Low",
    "additional_services": []
  },
  "risk_factors": {
    "hpv_positive": false,
    "smoking": false,
    "stds_history": false,
    "early_sexual_activity": false,
    "multiple_partners": false,
    "age_group": "25-35"
  }
}
```

1. **Age-Based Clinical Guidelines**: Ensures all patients ≥25 receive appropriate Pap smear screening
2. **HPV Vaccine Optimization**: Recommends vaccination for unvaccinated adults with low risk
3. **More Accurate Risk Assessment**: HPV testing provides crucial information
4. **Personalized Recommendations**: Tailored screening based on individual risk factors and age
5. **Better Clinical Outcomes**: Earlier detection and appropriate screening frequency
6. **Comprehensive Care**: Includes support services and education
7. **Evidence-Based**: Based on current medical guidelines for cervical cancer screening
8. **3-Dose HPV Schedule**: Proper vaccination guidance for adults who missed childhood vaccination


## Clinical Guidelines from Mundial Dennis❤️😂

1. **Age ≥25**: Mandatory Pap smear screening every 3 years (or 5 years with HPV co-testing)
2. **HPV Positive**: Immediate specialized care regardless of other factors
3. **Unvaccinated Adults >25 with Low Risk**: HPV vaccine recommendation (3-dose schedule)
4. **Age <25**: HPV vaccine priority, Pap smear starting at 25
5. **Risk-Based Frequency**: Higher risk = more frequent screening
