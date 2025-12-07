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
        """Loads the model artifacts."""
        try:
            # Determine path (handle local vs docker paths)
            base_path = "artifacts"
            if not os.path.exists(base_path):
                 base_path = "backend/artifacts"
            
            print(f"Loading artifacts from {os.path.abspath(base_path)}...")
            
            # Load Keras Model
            model_path = os.path.join(base_path, 'student_retention_model.keras')
            if not os.path.exists(model_path):
                # Fallback for updated filename if not renamed
                model_path = os.path.join(base_path, 'student_retention_model-2.keras')
            self.model = tf.keras.models.load_model(model_path)
            
            # Load Scaler
            scaler_path = os.path.join(base_path, 'scaler.joblib')
            if not os.path.exists(scaler_path):
                scaler_path = os.path.join(base_path, 'scaler-2.joblib')
            self.scaler = joblib.load(scaler_path)
            
            # Load Feature List (The final 75 columns expected by the model)
            features_path = os.path.join(base_path, 'model_features.json')
            if not os.path.exists(features_path):
                features_path = os.path.join(base_path, 'model_features-2.json')
            
            with open(features_path, 'r') as f:
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

        # 2. Logic: FastTrack students treated as 0 GPA for terms (Notebook Cell 8/9)
        # Assuming input FastTrack is 1 (Yes) or 2 (No) based on notebook data
        if df['FastTrack'].iloc[0] == 1:
            df['FirstTermGPA'] = 0.0
            df['SecondTermGPA'] = 0.0

        # 3. Create 'Missing' flags (Assuming 0 input implies missing for this specific context, 
        # or defaults. Notebook creates these from NaNs. We set to 0 for API inputs)
        for col in ["FirstTermGPA", "SecondTermGPA", "HighSchoolAverageMark", "MathScore", "EnglishGrade"]:
            df[f"Missing_{col.replace('HighSchoolAverageMark', 'HSMark')}"] = 0

        # 4. Feature Engineering
        # Continuous
        df['AvgFirstYearGPA'] = (df['FirstTermGPA'] + df['SecondTermGPA']) / 2.0
        df['HS_vs_FirstTerm_Gap'] = (df['HighSchoolAverageMark'] / 25.0) - df['FirstTermGPA']
        df['GPA_Progression'] = df['SecondTermGPA'] - df['FirstTermGPA']
        # Avoid division by zero
        df['HS_to_FirstTerm_Ratio'] = df['HighSchoolAverageMark'] / (df['FirstTermGPA'] + 1.0)

        # Risk Flags
        df['LowHSMark_flag'] = (df['HighSchoolAverageMark'] < 65).astype(int)
        df['LowFirstTermGPA_flag'] = (df['FirstTermGPA'] < 2.0).astype(int)

        # Binary Indicators
        df['FastTrack_isY'] = (df['FastTrack'] == 1).astype(int)
        df['Coop_isY'] = (df['Coop'] == 1).astype(int)

        # Binning HS Mark
        # bins=[-0.1, 60, 70, 80, 90, 200], labels=[0, 1, 2, 3, 4]
        df['HSMark_Bin'] = pd.cut(
            df['HighSchoolAverageMark'],
            bins=[-0.1, 60, 70, 80, 90, 200],
            labels=[0, 1, 2, 3, 4]
        ).astype(int)

        # Interaction Features (Strings)
        df['Funding_School'] = df['Funding'].astype(str) + "_" + df['School'].astype(str)
        df['Age_Residency'] = df['AgeGroup'].astype(str) + "_" + df['Residency'].astype(str)

        # 5. Prepare Categories for One-Hot Encoding
        cat_features = [
            "FirstLanguage", "Funding", "School", "Residency", "Gender", 
            "PrevEducation", "AgeGroup", "EnglishGrade", "HSMark_Bin",
            "Funding_School", "Age_Residency"
        ]
        
        # Ensure categorical cols are strings for get_dummies
        for col in cat_features:
            df[col] = df[col].astype(str)

        # 6. One-Hot Encoding
        df_processed = pd.get_dummies(df)

        # 7. Alignment: Reindex to match the training feature set exactly
        # This adds missing columns (filled with 0) and removes extra ones
        # Note: If self.feature_names contains raw names instead of OHE names, 
        # this step will fail. Ensure model_features.json contains the 75 expanded columns.
        try:
            df_aligned = df_processed.reindex(columns=self.feature_names, fill_value=0)
        except Exception as e:
            print("Warning: Feature alignment failed. Using processed dataframe as is.")
            df_aligned = df_processed

        # 8. Scale Numeric Columns
        numeric_cols_to_scale = [
            'FirstTermGPA', 'SecondTermGPA', 'HighSchoolAverageMark', 
            'MathScore', 'AvgFirstYearGPA', 'HS_vs_FirstTerm_Gap', 
            'GPA_Progression', 'HS_to_FirstTerm_Ratio'
        ]
        
        # Fill numeric NaNs with 0 before scaling
        df_aligned[numeric_cols_to_scale] = df_aligned[numeric_cols_to_scale].fillna(0)
        
        df_aligned[numeric_cols_to_scale] = self.scaler.transform(df_aligned[numeric_cols_to_scale])

        # 9. Predict
        model_input = df_aligned.values.astype(np.float32)
        
        # Check input shape match
        expected_shape = self.model.input_shape[1]
        if model_input.shape[1] != expected_shape:
             raise ValueError(f"Input shape mismatch. Model expects {expected_shape} features, got {model_input.shape[1]}. Please update 'model_features.json' with the list of 75 One-Hot Encoded feature names.")

        prediction_prob = self.model.predict(model_input)[0][0]
        
        # Sanitize Output
        prob = float(prediction_prob)
        if np.isnan(prob) or np.isinf(prob):
            prob = 0.0

        # Threshold Tuning
        threshold = 0.5
        prediction_class = int(prob > threshold)

        return {
            "prediction": prediction_class,
            "label": "Persist" if prediction_class == 1 else "Dropout Risk",
            "probability": prob,
            "risk_score": 1.0 - prob
        }