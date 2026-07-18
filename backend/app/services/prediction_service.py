import logging
from backend.app.ml.preprocessing import preprocess_input
from backend.app.ml.predictor import Predictor
from backend.app.ml.model_loader import model_loader
from backend.app.schemas.request import PredictionRequest

logger = logging.getLogger(__name__)

class PredictionService:
    def __init__(self):
        self.predictor = None

    def initialize(self):
        # Load model and scaler once on startup
        model, scaler = model_loader.load_assets()
        self.predictor = Predictor(model, scaler)

    def get_prediction(self, request_data: PredictionRequest) -> dict:
        if not self.predictor:
            logger.warning("Predictor not initialized. Initializing now...")
            self.initialize()
            
        # Convert Pydantic model to plain dict
        data_dict = request_data.model_dump()
        
        # Preprocess inputs
        input_df = preprocess_input(data_dict)
        
        # Run prediction
        prediction_label, confidence = self.predictor.predict(input_df)
        
        return {
            "prediction": prediction_label,
            "confidence": confidence
        }

# Singleton prediction service
prediction_service = PredictionService()
