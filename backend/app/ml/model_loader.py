import os
import pickle
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    def __init__(self):
        self.model = None
        self.scaler = None
        
        # Resolve path to root models/ directory
        base_dir = os.path.dirname(os.path.abspath(__file__)) # backend/app/ml
        project_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
        model_dir = os.path.join(project_root, "models")
        self.model_path = os.path.join(model_dir, "rf_alzheimers_model.pkl")
        self.scaler_path = os.path.join(model_dir, "scaler.pkl")

    def load_assets(self):
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Model loaded successfully from %s", self.model_path)
        except Exception as e:
            logger.error("Failed to load model from %s: %s", self.model_path, str(e))
            raise FileNotFoundError(f"ML model not found at {self.model_path}") from e

        try:
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("Scaler loaded successfully from %s", self.scaler_path)
        except Exception as e:
            logger.error("Failed to load scaler from %s: %s", self.scaler_path, str(e))
            raise FileNotFoundError(f"Scaler not found at {self.scaler_path}") from e
            
        return self.model, self.scaler

# Singleton instance
model_loader = ModelLoader()
