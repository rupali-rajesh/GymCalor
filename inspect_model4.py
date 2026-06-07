import pickle
import sklearn.compose._column_transformer as ct

class _RemainderColsList(list):
    pass
ct._RemainderColsList = _RemainderColsList

import warnings
warnings.filterwarnings('ignore')

with open('gradient_boosting_model.pkl', 'rb') as f:
    model = pickle.load(f)

if hasattr(model, 'feature_names_in_'):
    print("Features:", list(model.feature_names_in_))
else:
    print("No feature_names_in_ attribute. Printing first step:")
    print(model.steps[0])
