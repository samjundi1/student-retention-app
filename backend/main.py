from fastapi import FastAPI, HTTPException
from models import StudentData
from ai_service import RetentionModelService

# Initialize App
app = FastAPI(title="Student Retention AI API")

# Initialize AI Service
ai_service = RetentionModelService()

@app.get("/")
def home():
    return {"message": "Student Retention API is running"}

@app.post("/predict")
def predict_retention(data: StudentData):
    try:
        # Pass the Pydantic model as a dictionary to the service
        result = ai_service.predict(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))