# Package initializer for app
# Makes `app` importable as a package so `python -m app.app` works.
import warnings
# Ignore specific NumPy deprecation about setting array shape (joblib triggers this)
warnings.filterwarnings("ignore", message=".*Setting the shape on a NumPy array has been deprecated.*", category=DeprecationWarning)
# Also ignore DeprecationWarnings coming from joblib/numpy_pickle
warnings.filterwarnings("ignore", module="joblib.numpy_pickle", category=DeprecationWarning)

__all__ = ["services"]
