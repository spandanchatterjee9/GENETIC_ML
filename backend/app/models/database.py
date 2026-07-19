import os
import logging
import hashlib
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
Base = declarative_base()

# SHA-256 Password hashing helpers (dependency-free)
def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return f"{salt}:{pwd_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, pwd_hash = stored_hash.split(":")
        check_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return check_hash == pwd_hash
    except Exception:
        return False

# Database configuration and engine setup
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "mysql+pymysql://maria:maria@mariadb:3306/genetic_ml"
)

# Connect to database with SQLite fallback if MariaDB is unavailable
try:
    logger.info("Connecting to primary database at %s", DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL)
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        # 5 seconds timeout for MySQL connection attempts before falling back
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 5})
        # Test connection
        with engine.connect() as conn:
            pass
except Exception as e:
    logger.warning("Could not connect to database via %s, falling back to local SQLite: %s", DATABASE_URL, str(e))
    # Fallback to local SQLite file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(base_dir, "..", "..", ".."))
    sqlite_path = os.path.join(project_root, "database.db")
    fallback_url = f"sqlite:///{sqlite_path}"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DB Schema Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    predictions = relationship("PredictionRecord", back_populates="user")

class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Input Clinical Metrics
    age = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    blood_pressure = Column(Float, nullable=False)
    cholesterol = Column(Float, nullable=False)
    memory_complaints = Column(Integer, nullable=False) # 1 = Yes, 0 = No
    confusion = Column(Integer, nullable=False) # 1 = Yes, 0 = No
    forgetfulness = Column(Integer, nullable=False) # 1 = Yes, 0 = No
    
    # Model Output Metrics
    prediction_label = Column(String(50), nullable=False) # "High Risk" or "Low Risk"
    confidence_score = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")
