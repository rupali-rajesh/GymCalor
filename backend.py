from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
import warnings
import os

warnings.filterwarnings('ignore')

app = FastAPI(title="GymCalor API")

MODEL_PATH = "gradient_boosting_model.pkl"
model = None


@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("✅ Model loaded successfully.")
    else:
        print(f"⚠️  Model not found at {MODEL_PATH}")


class GymData(BaseModel):
    Age: int
    Gender: str
    Weight: float
    Height: float
    Max_BPM: float
    Avg_BPM: float
    Resting_BPM: float
    Session_Duration: float
    Workout_Type: str
    Fat_Percentage: float
    Water_Intake: float
    Workout_Frequency: int
    Experience_Level: int
    BMI: float


@app.post("/predict")
def predict_calories(data: GymData):
    if model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded.")

    input_df = pd.DataFrame([{
        'Age':                           data.Age,
        'Gender':                        data.Gender,
        'Weight (kg)':                   data.Weight,
        'Height (m)':                    data.Height,
        'Max_BPM':                       data.Max_BPM,
        'Avg_BPM':                       data.Avg_BPM,
        'Resting_BPM':                   data.Resting_BPM,
        'Session_Duration (hours)':      data.Session_Duration,
        'Workout_Type':                  data.Workout_Type,
        'Fat_Percentage':                data.Fat_Percentage,
        'Water_Intake (liters)':         data.Water_Intake,
        'Workout_Frequency (days/week)': data.Workout_Frequency,
        'Experience_Level':              data.Experience_Level,
        'BMI':                           data.BMI
    }])

    try:
        prediction = model.predict(input_df)[0]
        return {"predicted_calories_burned": float(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")


@app.get("/")
def root():
    return {"message": "GymCalor API is running 💪"}
