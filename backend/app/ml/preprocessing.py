import pandas as pd

def parse_yes_no(val):
    if isinstance(val, str):
        return 1 if val.lower() == 'yes' else 0
    return 1 if val else 0

def preprocess_input(data: dict) -> pd.DataFrame:
    # 1. Parse and Map form inputs to the 7 features
    age = float(data.get('Age', 0))
    bmi = float(data.get('BMI', 0))
    systolic_bp = float(data.get('BloodPressure', 0))
    chol_total = float(data.get('Cholesterol', 0))
    
    mem_comp = parse_yes_no(data.get('MemoryComplaints', 0))
    confusion = parse_yes_no(data.get('Confusion', 0))
    forget = parse_yes_no(data.get('Forgetfulness', 0))
    
    # 2. DataFrame wrapping to matching training feature names
    feature_cols = ['Age', 'BMI', 'SystolicBP', 'CholesterolTotal', 
                    'MemoryComplaints', 'Confusion', 'Forgetfulness']
    
    input_data = pd.DataFrame([[
        age, bmi, systolic_bp, chol_total, mem_comp, confusion, forget
    ]], columns=feature_cols)
    
    return input_data
