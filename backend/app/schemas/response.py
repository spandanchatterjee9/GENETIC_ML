from pydantic import BaseModel, Field
from typing import Dict, List, Optional

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

class AuthResponse(BaseModel):
    status: str = Field(..., description="Authentication outcome status")
    message: str = Field(..., description="Success or error description details")
    user_id: Optional[int] = Field(None, description="Hashed ID of the user session")
    username: Optional[str] = Field(None, description="Username of the user session")

class HistoryRecordResponse(BaseModel):
    id: int = Field(..., description="Unique record identifier")
    age: float = Field(..., description="Logged age")
    bmi: float = Field(..., description="Logged BMI")
    blood_pressure: float = Field(..., description="Logged blood pressure")
    cholesterol: float = Field(..., description="Logged cholesterol")
    memory_complaints: int = Field(..., description="Memory complaints flag")
    confusion: int = Field(..., description="Confusion flag")
    forgetfulness: int = Field(..., description="Forgetfulness flag")
    prediction_label: str = Field(..., description="Classification outcome")
    confidence_score: float = Field(..., description="Probability score")
    timestamp: str = Field(..., description="Datetime log stamp")

class HistoryListResponse(BaseModel):
    status: str = Field(..., description="Response outcome status")
    predictions: List[HistoryRecordResponse] = Field(..., description="Historical logs listing")

