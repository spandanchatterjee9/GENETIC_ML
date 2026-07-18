# Alzheimer's Risk Predictor (GENETIC_ML)

An enterprise-ready, production-grade Machine Learning classification application for early detection of Alzheimer's Disease. The system has been successfully migrated from Flask to a professional FastAPI architecture. It features strict request/response data validation via Pydantic, decoupled preprocessing, predictor, and model loading layers, and an interactive glassmorphism web user interface.

---

## 1. Technical Stack
- **Backend API**: FastAPI 0.111.0
- **Data Validation & Schemas**: Pydantic 2.7.4
- **Web Server Runner**: Uvicorn 0.30.1 (ASGI web server)
- **Machine Learning**: Scikit-Learn 1.8.0, NumPy 2.4.4, Pandas 3.0.2
- **Data Visualization**: Matplotlib (during pipeline generation), Chart.js (client-side dashboards)
- **Containerization**: Docker & Docker Compose
- **Client Frontend**: Vanilla HTML5, CSS3 (Modern Glassmorphic Dark UI), JavaScript (ES6 Fetch APIs)

---

## 2. API Endpoints

FastAPI automatically generates interactive OpenAPI documentation at `/docs`. Below is a summary of the served API endpoints:

| Method | Endpoint | Description | Request Payload | Response Schema |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | Serves the interactive user interface | None | `HTMLResponse` |
| **GET** | `/dashboard` | Serves the model analytics dashboard page | None | `HTMLResponse` |
| **GET** | `/health` | Returns application health status | None | `{"status": "healthy"}` |
| **GET** | `/metrics` | Returns mock model performance metrics & data points | None | `MetricsResponse` (json) |
| **POST** | `/predict` | Predicts Alzheimer's risk and returns confidence | `PredictionRequest` (json) | `PredictionResponse` (json) |

### Request payload validation (`POST /predict`)
```json
{
  "Age": 68.0,
  "BMI": 24.5,
  "BloodPressure": 120.0,
  "Cholesterol": 180.0,
  "MemoryComplaints": "Yes",
  "Confusion": "Yes",
  "Forgetfulness": "No"
}
```

### Response payload structure (`POST /predict`)
```json
{
  "prediction": "High Risk",
  "confidence": 57.0
}
```

---

## 3. Architecture & Folder Structure

We use a layered architecture separating routing, schemas, ML prediction, and business logic:

```
GENETIC_ML/
├── backend/                  # Isolated Python Backend
│   ├── app/                  # Application Core Packages
│   │   ├── api/
│   │   │   └── routes.py     # FastAPI routers (/health, /predict, /metrics)
│   │   ├── services/
│   │   │   └── prediction_service.py  # Coordinates ML preprocess & predict runs
│   │   ├── ml/
│   │   │   ├── model_loader.py  # Deserializes model & scaler once at startup
│   │   │   ├── preprocessing.py # Maps dropdowns and wraps inputs in DataFrames
│   │   │   ├── predictor.py     # Standardization and model inference logic
│   │   │   ├── alzheimers_pipeline.py  # Model training pipeline
│   │   │   └── evaluate_model.py       # Offline evaluation script
│   │   ├── schemas/
│   │   │   ├── request.py    # Pydantic request models
│   │   │   └── response.py   # Pydantic response models
│   │   ├── config/           # Application configurations placeholder
│   │   ├── utils/            # Shared utilities placeholder
│   │   ├── core/             # Application startup/lifecycle settings placeholder
│   │   └── main.py           # Entry ASGI server, template routing & lifespan setups
│   ├── requirements.txt      # FastAPI/ML library dependencies
│   └── Dockerfile            # Container construction script (Uvicorn-based)
├── frontend/                 # Decoupled Presentation Assets
│   ├── templates/            # HTML layouts (served via Jinja2Templates)
│   └── static/               # CSS and client JavaScript served via StaticFiles
├── data/                     # Raw CSV datasets
├── models/                   # Frozen production serialized model binaries
├── docs/                     # Documentation files
│   └── PROJECT_STRUCTURE.md  # Detailed overview of paths and request flows
├── outputs/                  # Training pipeline output figures and charts
└── docker-compose.yml        # Multi-service container orchestrator
```

---

## 4. Machine Learning Pipeline

### Model Loading & Startup
Model loading is decoupled into [model_loader.py](file:///C:/Users/spand/college/GENETIC_ML/backend/app/ml/model_loader.py). In `backend/app/main.py`, a FastAPI **lifespan handler** calls:
`prediction_service.initialize()`
This deserializes the Random Forest model and standardization scaler into memory *exactly once* during application startup, eliminating high I/O overhead on individual prediction requests.

### Preprocessing Layer
Parsed JSON inputs are preprocessed in [preprocessing.py](file:///C:/Users/spand/college/GENETIC_ML/backend/app/ml/preprocessing.py):
- Drops subjective values into binary signals (`Yes` -> `1`, `No` -> `0`).
- Wraps floats and binary indicators in a pandas DataFrame with matching column names:
  `['Age', 'BMI', 'SystolicBP', 'CholesterolTotal', 'MemoryComplaints', 'Confusion', 'Forgetfulness']`

### Prediction Inference
The standardized vectors are predicted in [predictor.py](file:///C:/Users/spand/college/GENETIC_ML/backend/app/ml/predictor.py):
- Applies `scaler.transform()` to fit inputs to training standard deviations.
- Runs `model.predict()` and `model.predict_proba()` to retrieve diagnosis risk class and classification confidence probabilities.

---

## 5. Installation & Setup

### Running Locally

#### 1. Setup Virtual Environment & Install Dependencies
Clone the repository, navigate to the project directory, create a virtual environment, and install dependencies:
```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate

# Install requirements
pip install -r backend/requirements.txt
```

#### 2. Run the Web Server
Launch the FastAPI development server as a python module to resolve paths properly:
```bash
python -m backend.app.main
```
Open a browser and navigate to `http://127.0.0.1:5000/`. You can now run early detection assessments, inspect interactive charts, and view the autogenerated Swagger API documentation at `http://127.0.0.1:5000/docs`.

---

## 6. Running with Docker

#### 1. Build and Run via Docker Compose
Build the image and launch the container in the background:
```bash
docker compose build --no-cache
docker compose up -d
```
The application will launch on `http://localhost:5000/`.

#### 2. Stop containers
```bash
docker compose down
```

---

## 7. Future Improvements
- **SQL Database Integration**: Implement databases (SQLAlchemy or SQLModel) under the `backend/app/models/` folder to persist assessment records, track diagnostic histories, and support authentication.
- **Pipeline Automation**: Integrate mlflow or DVC to track training runs, version model weights, and automate pipeline re-triggering.
- **Advanced Preprocessing Layers**: Introduce multi-class classification and dynamic pipeline transformers to streamline data ingestion workflows.
