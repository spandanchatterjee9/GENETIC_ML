from pydantic import BaseModel, Field
from typing import Union

class PredictionRequest(BaseModel):
    Age: Union[float, str] = Field(..., description="Patient age")
    BMI: Union[float, str] = Field(..., description="Patient body mass index")
    BloodPressure: Union[float, str] = Field(..., description="Patient systolic blood pressure (SystolicBP)")
    Cholesterol: Union[float, str] = Field(..., description="Patient cholesterol level (CholesterolTotal)")
    MemoryComplaints: Union[str, bool, int] = Field(..., description="Subjective memory complaints (Yes/No)")
    Confusion: Union[str, bool, int] = Field(..., description="Subjective confusion complaints (Yes/No)")
    Forgetfulness: Union[str, bool, int] = Field(..., description="Subjective forgetfulness complaints (Yes/No)")
