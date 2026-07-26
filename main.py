from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.api.dashboard import router as dashboard_router

app = FastAPI(
    title="GeoSentinel AI API"
)

# -----------------------------
# API Routes
# -----------------------------

app.include_router(dashboard_router)

# -----------------------------
# Static Files
# -----------------------------

app.mount(
    "/backend/outputs",
    StaticFiles(directory="backend/outputs"),
    name="outputs",
)

app.mount(
    "/datasets",
    StaticFiles(directory="datasets"),
    name="datasets",
)

# -----------------------------
# Health Check
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "GeoSentinel AI Backend Running"
    }