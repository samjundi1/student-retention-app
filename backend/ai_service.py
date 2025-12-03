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
            if not os.path.exists(base_path):
                 base_path = "backend/artifacts"
            
            print(f"Loading artifacts from {os.path.abspath(base_path)}...")
            
            self.model = tf.keras.models.load_model(os.path.join(base_path, 'student_retention_model.keras'))
            self.scaler = joblib.load(os.path.join(base_path, 'scaler.joblib'))
            
            with open(os.path.join(base_path, 'model_features.json'), 'r') as f:
                self.feature_names = json.load(f)
                
            self.artifacts_loaded = True
            print("Artifacts loaded successfully.")
        except Exception as e:
            print(f"Error loading artifacts: {e}")
            self.artifacts_loaded = False

    def predict(self, input_data: dict):
        if not self.artifacts_loaded:
            self.load_artifacts()
            if not self.artifacts_loaded:
                raise Exception("Model artifacts could not be loaded.")

        # 1. Convert to DataFrame
        df = pd.DataFrame([input_data])

        # 2. Feature Engineering
        df['AvgFirstYearGPA'] = (df['FirstTermGPA'] + df['SecondTermGPA']) / 2
        df['HS_vs_FirstTerm_Gap'] = (df['HighSchoolAverageMark'] / 25) - df['FirstTermGPA']
        df['LowHSMark_flag'] = (df['HighSchoolAverageMark'] < 65).astype(int)
        df['LowFirstTermGPA_flag'] = (df['FirstTermGPA'] < 2.0).astype(int)
        df['FastTrack_isY'] = (df['FastTrack'] == 1).astype(int)
        df['Coop_isY'] = (df['Coop'] == 1).astype(int)
        
        # 3. Align Columns
        try:
            df_processed = df[self.feature_names].copy()
        except KeyError as e:
            raise Exception(f"Missing feature columns in input: {e}")

        # 4. Scale ONLY Numeric Columns
        numeric_cols = [
            'FirstTermGPA', 'SecondTermGPA', 'HighSchoolAverageMark', 
            'MathScore', 'AvgFirstYearGPA', 'HS_vs_FirstTerm_Gap'
        ]
        
        # Check for missing values in numeric columns and fill with 0 to prevent NaN output
        df_processed[numeric_cols] = df_processed[numeric_cols].fillna(0)
        
        df_processed[numeric_cols] = self.scaler.transform(df_processed[numeric_cols])

        # 5. Predict
        # Force all data to float32 to satisfy Keras
        model_input = df_processed.values.astype(np.float32)
        prediction_prob = self.model.predict(model_input)[0][0]
        
        # --- FIX: Sanitize Output ---
        # Convert numpy types to python native types and handle NaN/Inf
        prob = float(prediction_prob)
        if np.isnan(prob) or np.isinf(prob):
            print("WARNING: Model predicted NaN/Inf. Defaulting to 0.0")
            prob = 0.0

        # 6. Threshold Tuning
        threshold = 0.5
        prediction_class = int(prob > threshold)

        return {
            "prediction": prediction_class,
            "label": "Persist" if prediction_class == 1 else "Dropout Risk",
            "probability": prob,
            "risk_score": 1.0 - prob
        }