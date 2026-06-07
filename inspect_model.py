import pickle
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

with open('gradient_boosting_model.pkl', 'rb') as f:
    model = pickle.load(f)

print(type(model))
if hasattr(model, 'feature_names_in_'):
    print("Features expected by model:")
    print(list(model.feature_names_in_))
else:
    print("No feature_names_in_ attribute found.")
