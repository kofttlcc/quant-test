
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegimeDetector:
    """
    Market Regime Detector based on Gaussian Mixture Model (GMM).
    Identifies 3 states: Bull, Bear, Volatile.
    Ported from legacy `prob_engine.py`.
    """
    def __init__(self, n_components=3):
        self.n_components = n_components
        self.model = GaussianMixture(n_components=n_components, covariance_type='full', random_state=42)
        self.is_fitted = False
        self.regime_map = {} # Mapping internal cluster ID to human semantic (0=Bull, 1=Volatile, 2=Bear)

    
    def fit(self, returns: np.ndarray, volatility: np.ndarray, macro_data: np.ndarray = None):
        """
        Fit the GMM model.
        Data shape: (n_samples, 2 + n_macro)
        """
        # Base features
        features = [returns, volatility]
        
        # Add macro features if present
        if macro_data is not None:
            # macro_data shape (n, k)
            if len(macro_data.shape) == 1:
                macro_data = macro_data.reshape(-1, 1)
            features.append(macro_data)
        
        X = np.column_stack(features)
        
        # Handle NaN/Inf
        mask = ~np.isnan(X).any(axis=1) & ~np.isinf(X).any(axis=1)
        X_clean = X[mask]
        
        if len(X_clean) < 50:
            logger.warning("Not enough data to train GMM. Skipping.")
            return
            
        self.model.fit(X_clean)
        self.is_fitted = True
        self._interpret_regimes_macro(X_clean, has_macro=(macro_data is not None))
        logger.info(f"Regime Detector fitted successfully (Features: {X.shape[1]}).")
        
    def _interpret_regimes_macro(self, X, has_macro=False):
        """
        Map clusters to semantic regimes using macro clues if available.
        Logic:
        1. Bull: High Return, Low/Med Vol (Low VIX)
        2. Bear: Negative Return, High Vol (High VIX)
        3. Volatile/Crisis: Extreme High Vol
        """
        means = self.model.means_ # shape (3, n_features)
        
        # We process 'Return' (idx 0) and 'Vol' (idx 1). 
        # If macro exists, idx 2 might be VIX.
        
        cluster_stats = []
        for i in range(self.n_components):
            mu_ret = means[i][0]
            mu_vol = means[i][1]
            cluster_stats.append((i, mu_ret, mu_vol))
            
        # Identify Bear (Lowest Return)
        bear_cluster = min(cluster_stats, key=lambda x: x[1])
        
        # Identify Bull (Highest Return)
        # Note: Sometimes "Bull" might have lower return than "Rebound" but generally lowest Vol.
        # Let's pivot to Volatility-first definition for stability.
        # Bull = Lowest Volatility cluster? 
        # Or Highest Sharpe?
        # Let's stick to Return for Bull.
        bull_cluster = max(cluster_stats, key=lambda x: x[1])
        
        # Identify Volatile (The remaining one)
        remaining = [c for c in cluster_stats if c[0] != bear_cluster[0] and c[0] != bull_cluster[0]]
        
        # Determine remaining
        # If we have 3 clusters, remaining is Volatile.
        volatile_cluster = remaining[0] if remaining else (None, 0, 0)
        
        # Conflict resolution: If Bull and Bear are same (rare), pick next best.
        if bull_cluster[0] == bear_cluster[0]:
             # This implies 1 cluster dominated range.
             # Reset mapping manually
             self.regime_map = {0: 1, 1: 1, 2: 1}
             return

        self.regime_map = {
            bull_cluster[0]: 0,      # Bull
            volatile_cluster[0]: 1,  # Volatile
            bear_cluster[0]: 2       # Bear
        }
        
    def predict(self, ret: float, vol: float, macro: list = None) -> str:
        """
        Predict regime for a single point.
        """
        if not self.is_fitted:
            return "Unknown"
            
        feats = [ret, vol]
        if macro:
            feats.extend(macro)
            
        X = np.array([feats])
        
        # Predict
        try:
             internal_regime = self.model.predict(X)[0]
             mapped_regime = self.regime_map.get(internal_regime, 1)
        except ValueError:
             # Feature mismatch?
             return "Error"
        
        desc_map = {0: "Bull", 1: "Volatile", 2: "Bear"}
        return desc_map.get(mapped_regime, "Unknown")

    def fit_predict_expanding(self, returns: np.ndarray, volatility: np.ndarray, macro_data: np.ndarray = None, min_window=60) -> np.ndarray:
        """
        Expanding window training with optional macro data.
        """
        n = len(returns)
        regimes = np.zeros(n, dtype=int) + 1 # Default to 1 (Volatile)
        
        logger.info(f"Starting Expanding Window GMM (N={n}, Min={min_window})...")
        
        refit_interval = 20
        has_macro = macro_data is not None
        
        if has_macro and len(macro_data.shape) == 1:
            macro_data = macro_data.reshape(-1, 1)
        
        for t in range(min_window, n):
            if (t - min_window) % refit_interval == 0:
                # Prepare training data [0:t]
                curr_ret = returns[:t]
                curr_vol = volatility[:t]
                
                features = [curr_ret, curr_vol]
                if has_macro:
                    features.append(macro_data[:t])
                
                X = np.column_stack(features)
                
                mask = ~np.isnan(X).any(axis=1) & ~np.isinf(X).any(axis=1)
                X_clean = X[mask]
                
                if len(X_clean) < 30:
                    continue
                    
                self.model.fit(X_clean)
                self._interpret_regimes_macro(X_clean, has_macro)
                
            # Predict t
            feat_t = [returns[t], volatility[t]]
            if has_macro:
                feat_t.extend(macro_data[t])
                
            X_curr = np.array([feat_t])
            
            if np.isnan(X_curr).any():
                regimes[t] = 1
                continue
                
            internal_pred = self.model.predict(X_curr)[0]
            regimes[t] = self.regime_map.get(internal_pred, 1)
            
        return regimes
