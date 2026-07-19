# API Documentation & Endpoint Architecture

This document describes the backend architecture, HTTP endpoints, Pydantic schemas, and data verification lifecycles of the FastAPI application.

---

## 1. Application Layer Layout

The backend is built around a decoupled architecture where request routing, data validation, business logic, and machine learning inference are strictly isolated:

- **`main.py`**: Initializes the FastAPI ASGI application, handles CORS middleware integration, mounts `/static` assets, registers `Jinja2Templates` (with custom Flask-compatible `url_for` template functions), and sets up the application lifespan handler.
- **`api/routes.py`**: Handles incoming HTTP routing, routes views (`/` and `/dashboard`), and exposes the backend API endpoints (`/health`, `/metrics`, `/predict`).
- **`schemas/`**:
  - `request.py`: Declares `PredictionRequest` modeling data types and descriptions.
  - `response.py`: Declares structure schemas for endpoint outputs (`PredictionResponse`, `MetricsResponse`, `HealthResponse`).
- **`services/prediction_service.py`**: A singleton service coordinating application flow.
- **`ml/`**: Encloses model assets, loader routines, preprocessors, and inference execution wrappers.

---

## 2. Interactive API Documentation (Swagger)

FastAPI autogenerates standard OpenAPI specifications. When the server is active, you can access the visual interface at:
`http://127.0.0.1:5000/docs`

This interactive interface allows you to test endpoint requests directly in the browser.

---

## 3. Endpoint Reference

### Health Check Endpoint
- **URL**: `/health`
- **Method**: `GET`
- **Response Schema**: `HealthResponse`
- **Response Output**:
  ```json
  {
    "status": "healthy"
  }
  ```

### Performance Metrics Endpoint
- **URL**: `/metrics`
- **Method**: `GET`
- **Response Schema**: `MetricsResponse`
- **Response Output**: Returns a JSON representation of model comparisons, feature importances, ROC curve coordinates, and confusion matrices.

### Risk Prediction Endpoint
- **URL**: `/predict`
- **Method**: `POST`
- **Request Schema**: `PredictionRequest`
- **Response Schema**: `PredictionResponse`

#### Sample JSON Payload
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
*Note: Pydantic handles string-to-numeric coercion automatically, accepting parameters as numerical floats/integers or string representations (e.g. `"68"`)*

#### Sample Response Output (200 OK)
```json
{
  "prediction": "High Risk",
  "confidence": 57.0
}
```

---

## 4. Lifecycle & Request Flow

The following describes how the application handles requests:

```
[HTTP Client Request] 
         │
         ▼
[Pydantic Type Validation]  ─── (Invalid Inputs) ───► [HTTP 422 ValidationError]
         │
         ▼
[api/routes.py Router]
         │
         ▼
[services/prediction_service.py]
         │
         ▼
[ml/preprocessing.py]  ───► Map "Yes"/"No" to 1/0 & Build pandas DataFrame
         │
         ▼
[ml/predictor.py]      ───► Standardize features via StandardScaler
         │
         ▼
[ml/predictor.py]      ───► Model predict() & predict_proba()
         │
         ▼
[HTTP Client Response JSON]
```

---

## 5. System Error Handling

- **Pydantic Validation Failures**: If request parameters violate input definitions (e.g., missing fields or invalid types), FastAPI returns a `422 Unprocessable Entity` response containing the exact parameters causing the validation failure.
- **Model Inaccessibility**: If model weight pickles are missing or corrupted on startup, the loader service logs the error and raises a `FileNotFoundError`, preventing the server from starting.
- **Runtime Errors**: General exceptions occurring during preprocessing or prediction are caught by the router error handler, returning an `HTTP 400 Bad Request` with the exception details:
  ```json
  {
    "detail": "Error description message"
  }
  ```
