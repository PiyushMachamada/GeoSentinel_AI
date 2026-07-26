from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api.status import router as status_router
from backend.api.satellite import router as satellite_router
from backend.api.change_detection import router as change_router
# from backend.api.data_collection import router as data_collection_router 
from backend.api.dashboard import router as dashboard_router
from backend.api.aoi import router as aoi_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="GeoSentinel AI",
    description="Multimodal Earth Observation Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status_router)
app.include_router(satellite_router)
app.include_router(change_router)
# app.include_router(data_collection_router)
app.include_router(dashboard_router)
app.include_router(aoi_router)
app.mount(
    "/outputs",
    StaticFiles(directory="backend/outputs"),
    name="outputs"
)
@app.get("/")
def home():
    return {
        "message": "GeoSentinel AI Backend Running"
    }