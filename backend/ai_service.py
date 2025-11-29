import joblib
import json
import pandas as pd
import numpy as np
import tensorflow as tf
import os

class RetentionModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.artifacts_loaded = False

    def load_artifacts(self):
        """Loads the model artifacts only when needed."""
        try:
            # Paths relative to where uvicorn is run (backend/)
            base_path = "artifacts"
            
            print(f"Loading artifacts from {os.path.abspath(base_path)}...")
            
            self.model = tf.keras.models.load_model(os.path.join(base_path, 'student_retention_model.keras'))
            self.scaler = joblib.load(os.path.join(base_path, 'scaler.joblib'))
            
            with open(os.path.join(base_path, 'model_features.json'), 'r') as f:
                self.feature_names = json.load(f)
                
            self.artifacts_loaded = True
            print("Artifacts loaded successfully.")
        except Exception as e:
            print(f"Error loading artifacts: {e}")
            # We don't raise here to allow the app to start even if models are missing initially
            self.artifacts_loaded = False

    def predict(self, input_data: dict):
        if not self.artifacts_loaded:
            self.load_artifacts()
            if not self.artifacts_loaded:
                raise Exception("Model artifacts could not be loaded. Check 'backend/artifacts' folder.")

        # 1. Convert to DataFrame
        df = pd.DataFrame([input_data])

        # 2. Feature Engineering (Must match training logic exactly)
        df['AvgFirstYearGPA'] = (df['FirstTermGPA'] + df['SecondTermGPA']) / 2
        df['HS_vs_FirstTerm_Gap'] = (df['HighSchoolAverageMark'] / 25) - df['FirstTermGPA']
        df['LowHSMark_flag'] = (df['HighSchoolAverageMark'] < 65).astype(int)
        df['LowFirstTermGPA_flag'] = (df['FirstTermGPA'] < 2.0).astype(int)
        df['FastTrack_isY'] = (df['FastTrack'] == 1).astype(int)
        df['Coop_isY'] = (df['Coop'] == 1).astype(int)
        
        # Interaction Term
        df['Intl_English_Risk'] = ((df['Residency'] == 2) & (df['EnglishGrade'] < 5)).astype(int)

        # 3. Align Columns
        df_processed = df[self.feature_names]

        # 4. Scale
        X_scaled = self.scaler.transform(df_processed)

        # 5. Predict
        prediction_prob = self.model.predict(X_scaled)[0][0]
        
        # 6. Threshold Tuning (0.65 as optimized)
        threshold = 0.65
        prediction_class = int(prediction_prob > threshold)

        return {
            "prediction": prediction_class,
            "label": "Persist" if prediction_class == 1 else "Dropout Risk",
            "probability": float(prediction_prob),
            "risk_score": float(1 - prediction_prob)
        }