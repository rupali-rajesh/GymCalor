import pickle
import sklearn.compose._column_transformer as ct
from collections import namedtuple

# Monkey patch _RemainderColsList
if not hasattr(ct, '_RemainderColsList'):
    ct._RemainderColsList = property
    # Or just an empty class? Let's check what it was. It was a class or namedtuple in scikit-learn < 1.3
    # Wait, usually namedtuple('_RemainderColsList', []) won't unpickle correctly if it expects a type.
    pass

import warnings
warnings.filterwarnings('ignore')

try:
    with open('gradient_boosting_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Loaded model successfully with monkey patch!")
except Exception as e:
    print(f"Error: {repr(e)}")
