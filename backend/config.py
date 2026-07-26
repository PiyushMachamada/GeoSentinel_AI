import os

# ==========================================
# GeoSentinel Configuration
# ==========================================

# Monitoring
MONITOR_INTERVAL_MINUTES = 1
MAX_CLOUD_COVER = 30

# Qwen
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate",
)

QWEN_MODEL = os.getenv(
    "QWEN_MODEL",
    "qwen2.5:7b",
)

# Outputs
OUTPUT_DIR = "backend/outputs"

# Database
DATABASE_PATH = "backend/database/geosentinel.db"

# Logging
LOG_LEVEL = "INFO"