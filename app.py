import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the trained model and scaler globally
model = None
scaler = None

def load_ml_assets():
    global model, scaler
    try:
        with open('rf_alzheimers_model.pkl', 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully.")
    except FileNotFoundError:
        print("Warning: Model file not found. Run alzheimers_pipeline.py first.")

    try:
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        print("Scaler loaded successfully.")
    except FileNotFoundError:
        print("Warning: Scaler file not found. Run alzheimers_pipeline.py first.")

load_ml_assets()

@app.route('/')
def home():
    # Serve the frontend
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Try reloading if missing (helps with testing if pipeline was run afterward)
    if not model or not scaler:
        load_ml_assets()
        
    if not model or not scaler:
        return jsonify({"error": "ML model or scaler is missing. Please run the training pipeline first."}), 500

    try:
        data = request.json
        print("Received prediction request:", data)
        
        # 1. Parse and Map form inputs to the 7 features
        age = float(data.get('Age', 0))
        bmi = float(data.get('BMI', 0))
        systolic_bp = float(data.get('BloodPressure', 0))       # Mapped as requested
        chol_total = float(data.get('Cholesterol', 0))          # Mapped as requested
        
        # Helper to convert dropdown "yes" / "no" to 1 / 0
        def parse_yes_no(val):
            if isinstance(val, str):
                return 1 if val.lower() == 'yes' else 0
            return 1 if val else 0
            
        mem_comp = parse_yes_no(data.get('MemoryComplaints', 0))
        confusion = parse_yes_no(data.get('Confusion', 0))
        forget = parse_yes_no(data.get('Forgetfulness', 0))
        
        # 2. DataFrame wrapping to matching training feature names
        feature_cols = ['Age', 'BMI', 'SystolicBP', 'CholesterolTotal', 
                        'MemoryComplaints', 'Confusion', 'Forgetfulness']
        
        input_data = pd.DataFrame([[
            age, bmi, systolic_bp, chol_total, mem_comp, confusion, forget
        ]], columns=feature_cols)

        # 3. Standard Scaling exactly as handled in the training script
        input_scaled = scaler.transform(input_data)
        input_df = pd.DataFrame(input_scaled, columns=feature_cols)

        # 4. Predict
        prediction_val = model.predict(input_df)[0]
        probs = model.predict_proba(input_df)[0]
        
        # Scikit-learn outputs probability for each class [prob_0, prob_1]
        prob_1 = probs[1] 

        prediction_label = "High Risk" if prediction_val == 1 else "Low Risk"
        # Confidence is the probability of the predicted class
        confidence = float(prob_1 * 100) if prediction_val == 1 else float(probs[0] * 100)

        # 5. Return HTTP Response
        return jsonify({
            "prediction": prediction_label,
            "confidence": round(confidence, 1)
        })

    except Exception as e:
        print("Error during prediction:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
