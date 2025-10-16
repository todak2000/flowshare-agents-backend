"""
Shared configuration for all agents
"""
import os
from typing import Optional
from dotenv import load_dotenv

# This line reads the .env file and loads the variables into the environment
load_dotenv()

class Config:
    """Environment configuration"""

    # Google Cloud
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "back-allocation")
    REGION: str = os.getenv("GCP_REGION", "europe-west1")

    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

    # Firestore Collections
    COLLECTION_PRODUCTION_ENTRIES: str = "production_entries"
    COLLECTION_TERMINAL_RECEIPTS: str = "terminal_receipts"
    COLLECTION_RECONCILIATION_RUNS: str = "reconciliation_runs"
    COLLECTION_NOTIFICATIONS: str = "notifications"
    COLLECTION_AGENT_LOGS: str = "agent_logs"

    # Agent URLs (set after deployment)
    AUDITOR_AGENT_URL: Optional[str] = os.getenv("AUDITOR_AGENT_URL")
    ACCOUNTANT_AGENT_URL: Optional[str] = os.getenv("ACCOUNTANT_AGENT_URL")
    COMMUNICATOR_AGENT_URL: Optional[str] = os.getenv("COMMUNICATOR_AGENT_URL")

    # Validation thresholds
    BSW_MIN: float = 0.0
    BSW_MAX: float = 10.0
    TEMP_MIN: float = 60.0
    TEMP_MAX: float = 150.0
    API_GRAVITY_MIN: float = 15.0
    API_GRAVITY_MAX: float = 45.0

    # Anomaly detection
    Z_SCORE_THRESHOLD: float = 2.0  # Standard deviations
    MIN_HISTORICAL_SAMPLES: int = 5


config = Config()
