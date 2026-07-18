from pydantic import BaseModel, Field

class PredictionResponse(BaseModel):
    prediction: str = Field(..., description="Diagnosis risk level (High Risk / Low Risk)")
    confidence: float = Field(..., description="Probability confidence percentage")

class MetricsResponse(BaseModel):
    comparison: dict = Field(..., description="Model comparison metrics")
    roc: dict = Field(..., description="ROC curves data points")
    feature_importance: dict = Field(..., description="Feature importances")
    matrices: dict = Field(..., description="Model confusion matrices")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Application health status")
