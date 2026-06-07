"""
Run this ONCE to create a fresh model compatible with your Python/sklearn version.
Just run: python retrain_model.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import pickle
import warnings
warnings.filterwarnings('ignore')

print("Creating training data...")

np.random.seed(42)
N = 973

genders      = np.random.choice(['Male', 'Female','Non-binary','Prefer not to say'], N, p=[0.52, 0.48, 0.02, 0.02])
workout_types = np.random.choice(['Cardio', 'Strength', 'Yoga', 'HIIT'], N, p=[0.25, 0.30, 0.20, 0.25])
exp_levels   = np.random.choice([1, 2, 3], N, p=[0.33, 0.39, 0.28])

age     = np.random.randint(18, 60, N)
weight  = np.where(genders == 'Male', np.random.normal(80, 12, N), np.random.normal(65, 10, N))
height  = np.where(genders == 'Male', np.random.normal(1.78, 0.07, N), np.random.normal(1.65, 0.06, N))
fat_pct = np.clip(np.where(genders == 'Male', np.random.normal(18, 5, N), np.random.normal(25, 5, N)), 5, 45)
bmi     = weight / (height ** 2)

resting_bpm = np.random.normal(65, 8, N).clip(45, 100)
max_bpm     = np.random.normal(175, 12, N).clip(140, 210)
avg_bpm     = resting_bpm + (max_bpm - resting_bpm) * np.random.uniform(0.45, 0.80, N)

duration = np.random.uniform(0.5, 3.0, N)
water    = np.random.uniform(0.5, 3.5, N)
freq     = np.random.choice([2, 3, 4, 5, 6], N, p=[0.15, 0.30, 0.30, 0.15, 0.10])

base_cal = (
    0.6 * weight
    + 4.0 * (avg_bpm - resting_bpm)
    + 180 * duration
    + 10 * (max_bpm - avg_bpm)
    - 0.5 * fat_pct
    + 5 * exp_levels
    + 3 * freq
)
type_bonus = np.where(workout_types == 'HIIT', 80,
             np.where(workout_types == 'Cardio', 40,
             np.where(workout_types == 'Strength', 20, -20)))
calories = (base_cal + type_bonus + np.random.normal(0, 20, N)).clip(80, 1200)

df = pd.DataFrame({
    'Age':                          age,
    'Gender':                       genders,
    'Weight (kg)':                  weight.round(1),
    'Height (m)':                   height.round(2),
    'Max_BPM':                      max_bpm.round(0).astype(int),
    'Avg_BPM':                      avg_bpm.round(0).astype(int),
    'Resting_BPM':                  resting_bpm.round(0).astype(int),
    'Session_Duration (hours)':     duration.round(2),
    'Workout_Type':                 workout_types,
    'Fat_Percentage':               fat_pct.round(1),
    'Water_Intake (liters)':        water.round(2),
    'Workout_Frequency (days/week)': freq,
    'Experience_Level':             exp_levels,
    'BMI':                          bmi.round(2),
    'Calories_Burned':              calories.round(1)
})

print(f"Dataset created: {len(df)} records")

# Build pipeline
cat_features = ['Gender', 'Workout_Type']
num_features = [
    'Age', 'Weight (kg)', 'Height (m)', 'Max_BPM', 'Avg_BPM',
    'Resting_BPM', 'Session_Duration (hours)', 'Fat_Percentage',
    'Water_Intake (liters)', 'Workout_Frequency (days/week)',
    'Experience_Level', 'BMI'
]

preprocessor = ColumnTransformer([
    ('cat', OneHotEncoder(drop='first', sparse_output=False), cat_features)
], remainder='passthrough')

model = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=4,
    min_samples_split=5,
    min_samples_leaf=3,
    subsample=0.8,
    random_state=42
)

pipeline = Pipeline([('pre', preprocessor), ('gbr', model)])

X = df.drop('Calories_Burned', axis=1)
y = df['Calories_Burned']

print("Training model...")
pipeline.fit(X, y)

# Save model
with open('gradient_boosting_model.pkl', 'wb') as f:
    pickle.dump(pipeline, f)

print("✅ Model trained and saved as gradient_boosting_model.pkl")
print(f"   sklearn version: {__import__('sklearn').__version__}")

# Test it works
test = pd.DataFrame([{
    'Age': 25, 'Gender': 'Male', 'Weight (kg)': 70.0, 'Height (m)': 1.75,
    'Max_BPM': 180, 'Avg_BPM': 140, 'Resting_BPM': 65,
    'Session_Duration (hours)': 1.0, 'Workout_Type': 'HIIT',
    'Fat_Percentage': 15.0, 'Water_Intake (liters)': 1.5,
    'Workout_Frequency (days/week)': 3, 'Experience_Level': 2, 'BMI': 22.86
}])
result = pipeline.predict(test)[0]
print(f"   Test prediction: {result:.1f} kcal ✅")
print("\nNow run: python run_app.py")
