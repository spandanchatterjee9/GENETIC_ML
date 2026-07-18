from fastapi import APIRouter, HTTPException
from backend.app.schemas.request import PredictionRequest
from backend.app.schemas.response import PredictionResponse, MetricsResponse, HealthResponse
from backend.app.services.prediction_service import prediction_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "healthy"}

@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        result = prediction_service.get_prediction(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics", response_model=MetricsResponse)
def metrics():
    # Mock data reflecting a realistic Alzheimer's prediction ML pipeline
    data = {
        "comparison": {
            "Random Forest": {"accuracy": 0.93, "precision": 0.94, "recall": 0.91, "f1": 0.92},
            "Logistic Regression": {"accuracy": 0.85, "precision": 0.86, "recall": 0.83, "f1": 0.84},
            "Decision Tree": {"accuracy": 0.88, "precision": 0.87, "recall": 0.89, "f1": 0.88},
            "KNN": {"accuracy": 0.82, "precision": 0.81, "recall": 0.84, "f1": 0.82}
        },
        "roc": {
            "fpr": [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0],
            "Random Forest": [0.0, 0.88, 0.94, 0.97, 0.99, 1.0, 1.0],
            "Logistic Regression": [0.0, 0.70, 0.82, 0.88, 0.93, 0.97, 1.0],
            "Decision Tree": [0.0, 0.75, 0.85, 0.91, 0.95, 0.98, 1.0],
            "KNN": [0.0, 0.65, 0.78, 0.85, 0.90, 0.94, 1.0]
        },
        "feature_importance": {
            "features": ["MemoryComplaints", "Age", "Confusion", "Forgetfulness", "SystolicBP", "Cholesterol", "BMI"],
            "importance": [0.35, 0.22, 0.18, 0.12, 0.06, 0.04, 0.03]
        },
        "matrices": {
            "Random Forest": {"tp": 145, "tn": 150, "fp": 8, "fn": 12},
            "Logistic Regression": {"tp": 125, "tn": 140, "fp": 18, "fn": 32},
            "Decision Tree": {"tp": 138, "tn": 145, "fp": 13, "fn": 19},
            "KNN": {"tp": 120, "tn": 135, "fp": 23, "fn": 37}
        }
    }
    return data
