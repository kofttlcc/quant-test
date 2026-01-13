
import numpy as np
import pandas as pd
import logging
import pickle
import os
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.base import clone
import sys

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from src.models.validation import CombinatorialPurgedKFold
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLPTrendModel:
    """
    MLP for Trend Prediction (Sklearn version).
    Fallback for when TensorFlow is not available.
    Integrates Purged CV.
    """
    def __init__(self, sequence_length=60, learning_rate=0.001):
        self.sequence_length = sequence_length
        self.learning_rate = learning_rate
        # Sklearn MLP
        self.model = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation='relu',
            solver='adam',
            learning_rate_init=learning_rate,
            max_iter=200,
            early_stopping=False, # We control CV
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.best_model = None
        self.on_fold_end = None # Callable accepting (fold, score)
        
    def fit_cv(self, X, y):
        """
        Train with Purged CV.
        """
        # 1. Normalize
        X_scaled = self.scaler.fit_transform(X)
        
        # 2. CV Loop
        cv = CombinatorialPurgedKFold(n_splits=5, n_test_splits=1, purge_window=5)
        
        best_score = -np.inf
        total_folds = 5
        
        for i, (train_idx, val_idx) in enumerate(cv.split(X_scaled)):
            X_train = X_scaled[train_idx]
            y_train = y[train_idx]
            X_val = X_scaled[val_idx]
            y_val = y[val_idx]
            
            # Clone model to start fresh
            fold_model = clone(self.model)
            fold_model.fit(X_train, y_train)
            
            score = fold_model.score(X_val, y_val)
            logger.info(f"Fold {i} Acc: {score:.4f}")
            
            if self.on_fold_end:
                self.on_fold_end(i, total_folds, score)
            
            if score > best_score:
                best_score = score
                self.best_model = fold_model
                
        # Finalize
        if self.best_model:
            logger.info(f"Best CV Acc: {best_score:.4f}")
            self.model = self.best_model
            self.is_fitted = True
        else:
             logger.warning("CV failed.")

    def predict_proba(self, X):
        if not self.is_fitted:
            return np.zeros(len(X))
        X_scaled = self.scaler.transform(X)
        # Class 1 prob
        return self.model.predict_proba(X_scaled)[:, 1]

class MLPPredictor:
    def __init__(self, sequence_length=60, model_path=None):
        self.sequence_length = sequence_length
        self.model = MLPTrendModel(sequence_length)
        self.model_path = model_path or os.environ.get('ML_MODEL_PATH', 'temp/ml_models/mlp_sklearn.pkl')
        self.on_fold_end = None
        
    def create_features(self, data: np.ndarray):
        xs, ys = [], []
        for i in range(len(data) - self.sequence_length - 1):
            x = data[i : i+self.sequence_length]
            if len(x) > 0 and x[0] != 0:
                x = (x / x[0]) - 1.0
            
            y_val = data[i+self.sequence_length] - data[i+self.sequence_length-1]
            y = 1 if y_val > 0 else 0
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)
        
    def train(self, df: pd.DataFrame, save=True):
        if 'Close' not in df.columns: return
        data = df['Close'].values
        X, y = self.create_features(data)
        if len(X) == 0: return
        
        logger.info(f"Training Sklearn MLP with Purged CV on {len(X)} samples...")
        self.model.on_fold_end = self.on_fold_end
        self.model.fit_cv(X, y)
        
        if save:
            self.save_model()
            
    def predict(self, sequence: np.ndarray):
        if len(sequence) > 0 and sequence[0] != 0:
            seq = (sequence / sequence[0]) - 1.0
        else:
            seq = sequence
        return self.model.predict_proba(seq.reshape(1, -1))[0]
        
    def save_model(self):
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
        except Exception:
            pass

    def load_model(self):
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            return True
        except Exception:
            return False
            
    def generate_signals(self, df):
        start_idx = self.sequence_length
        strat_df = df.copy()
        strat_df['Signal'] = 0
        
        if self.model.is_fitted:
             prices = df['Close'].values
             for i in range(start_idx, len(prices)):
                 seq = prices[i-self.sequence_length:i]
                 prob = self.predict(seq)
                 if prob > 0.52: strat_df.iloc[i, strat_df.columns.get_loc('Signal')] = 1
                 elif prob < 0.48: strat_df.iloc[i, strat_df.columns.get_loc('Signal')] = -1
        
        strat_df['Position'] = strat_df['Signal'].ffill().fillna(0)
        return strat_df

# Aliases
LSTMTrendModel = MLPTrendModel
LSTMPredictor = MLPPredictor

if __name__ == "__main__":
    print("--- SELF-TEST: lstm_predictor.py (Sklearn + Purged CV) ---")
    dates = pd.date_range("2023-01-01", periods=200)
    prices = 100 + np.cumsum(np.random.normal(0, 1, 200))
    df = pd.DataFrame({'Close': prices}, index=dates)
    
    pred = MLPPredictor(sequence_length=10)
    pred.train(df, save=False)
    
    if pred.model.is_fitted:
        print("[TEST] SUCCESS: Model fitted using CV.")
    else:
        print("[TEST] FAILURE: Model not fitted.")
