import pickle
import sklearn.compose._column_transformer as ct

# Define a class matching what scikit-learn expected. It was probably a class or list subclass.
class _RemainderColsList(list):
    pass

ct._RemainderColsList = _RemainderColsList

import warnings
warnings.filterwarnings('ignore')

try:
    with open('gradient_boosting_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Loaded model successfully with monkey patch class _RemainderColsList(list)!")
    print(type(model))
except Exception as e:
    print(f"Error: {repr(e)}")
