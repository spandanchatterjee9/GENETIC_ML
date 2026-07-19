import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import pass_context

from backend.app.api.routes import router as api_router
from backend.app.services.prediction_service import prediction_service

# Setup structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("backend")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

template_dir = os.path.join(PROJECT_ROOT, "frontend", "templates")
static_dir = os.path.join(PROJECT_ROOT, "frontend", "static")

# Lifespan context manager for loading ML assets once on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    try:
        from backend.app.models.database import Base, engine
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database tables: %s", str(e))

    logger.info("Initializing ML models and preprocessors...")
    try:
        prediction_service.initialize()
        logger.info("ML models loaded successfully.")
    except Exception as e:
        logger.error("Failed to load ML models at startup: %s", str(e))
    yield
    logger.info("Shutting down application...")

app = FastAPI(title="Alzheimer's Risk Predictor API", lifespan=lifespan)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates setup
templates = Jinja2Templates(directory=template_dir)

# Override / define custom url_for global to handle Flask-compatible signatures in template files
@pass_context
def jinja2_url_for(context: dict, name: str, **path_params):
    request = context.get("request")
    if not request:
        raise ValueError("Request object not found in template context")
    if name == "static" and "filename" in path_params:
        path_params["path"] = path_params.pop("filename")
    return str(request.url_for(name, **path_params))

templates.env.globals["url_for"] = jinja2_url_for

# HTML template serving endpoints (matching Flask routes exactly)
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/dashboard", response_class=HTMLResponse)
@app.get("/dashboard.html", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

# Include API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=True)
