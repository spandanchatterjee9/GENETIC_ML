import pandas as pd
from typing import Tuple

class Predictor:
    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler

    def predict(self, input_df: pd.DataFrame) -> Tuple[str, float]:
        feature_cols = ['Age', 'BMI', 'SystolicBP', 'CholesterolTotal', 
                        'MemoryComplaints', 'Confusion', 'Forgetfulness']
                        
        # 3. Standard Scaling exactly as handled in the training script
        input_scaled = self.scaler.transform(input_df)
        scaled_df = pd.DataFrame(input_scaled, columns=feature_cols)

        # 4. Predict
        prediction_val = self.model.predict(scaled_df)[0]
        probs = self.model.predict_proba(scaled_df)[0]
        
        prob_1 = probs[1] 

        prediction_label = "High Risk" if prediction_val == 1 else "Low Risk"
        # Confidence is the probability of the predicted class
        confidence = float(prob_1 * 100) if prediction_val == 1 else float(probs[0] * 100)
        
        return prediction_label, round(confidence, 1)
