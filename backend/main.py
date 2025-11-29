from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from models import StudentData
from ai_service import RetentionModelService
from contextlib import asynccontextmanager
import os

# Initialize AI Service globally
ai_service = RetentionModelService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load artifacts on startup
    print("Loading model artifacts...")
    ai_service.load_artifacts()
    if not ai_service.artifacts_loaded:
        print("WARNING: Model artifacts failed to load. API will return errors for predictions.")
    yield
    # Clean up resources on shutdown (if needed)
    print("Shutting down...")

# Initialize App with lifespan
app = FastAPI(title="Student Retention AI API", lifespan=lifespan)

# --- NEW: Add CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (e.g., file://, localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- UPDATED: Serve Frontend on Root ---
@app.get("/", response_class=HTMLResponse)
def home():
    # Ensure your index.html is in a folder named 'static' or just read it
    try:
        with open("frontend/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Frontend not found. Make sure frontend/index.html exists.</h1>"

@app.post("/predict")
def predict_retention(data: StudentData):
    try:
        # Pass the Pydantic model as a dictionary to the service
        result = ai_service.predict(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))