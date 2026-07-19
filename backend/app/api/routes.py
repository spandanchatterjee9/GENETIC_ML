from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.schemas.request import PredictionRequest, UserAuth
from backend.app.schemas.response import (
    PredictionResponse, MetricsResponse, HealthResponse, 
    AuthResponse, HistoryListResponse, HistoryRecordResponse
)
from backend.app.services.prediction_service import prediction_service
from backend.app.models.database import get_db, User, PredictionRecord, hash_password, verify_password

router = APIRouter()

def to_binary(val) -> int:
    if isinstance(val, str):
        return 1 if val.lower() in ("yes", "true", "1") else 0
    if isinstance(val, bool):
        return 1 if val else 0
    if isinstance(val, int):
        return 1 if val > 0 else 0
    return 0

@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "healthy"}

@router.post("/api/auth/register", response_model=AuthResponse)
def register(auth: UserAuth, db: Session = Depends(get_db)):
    # Check if username exists
    existing_user = db.query(User).filter(User.username == auth.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password and save user
    hashed = hash_password(auth.password)
    user = User(username=auth.username, password_hash=hashed)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
        return {
            "status": "success", 
            "message": "User registered successfully", 
            "user_id": user.id,
            "username": user.username
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/auth/login", response_model=AuthResponse)
def login(auth: UserAuth, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == auth.username).first()
    if not user or not verify_password(auth.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {
        "status": "success", 
        "message": "Logged in successfully", 
        "user_id": user.id,
        "username": user.username
    }

@router.get("/api/predictions", response_model=HistoryListResponse)
def get_predictions(user_id: int, db: Session = Depends(get_db)):
    records = db.query(PredictionRecord).filter(PredictionRecord.user_id == user_id).order_by(PredictionRecord.timestamp.desc()).all()
    
    history = []
    for r in records:
        history.append(HistoryRecordResponse(
            id=r.id,
            age=r.age,
            bmi=r.bmi,
            blood_pressure=r.blood_pressure,
            cholesterol=r.cholesterol,
            memory_complaints=r.memory_complaints,
            confusion=r.confusion,
            forgetfulness=r.forgetfulness,
            prediction_label=r.prediction_label,
            confidence_score=r.confidence_score,
            timestamp=r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ))
        
    return {"status": "success", "predictions": history}

@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    try:
        result = prediction_service.get_prediction(request)
        
        # Save prediction run in the database
        record = PredictionRecord(
            user_id=request.user_id,
            age=float(request.Age),
            bmi=float(request.BMI),
            blood_pressure=float(request.BloodPressure),
            cholesterol=float(request.Cholesterol),
            memory_complaints=to_binary(request.MemoryComplaints),
            confusion=to_binary(request.Confusion),
            forgetfulness=to_binary(request.Forgetfulness),
            prediction_label=result["prediction"],
            confidence_score=result["confidence"]
        )
        db.add(record)
        db.commit()
        
        return result
    except Exception as e:
        db.rollback()
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

