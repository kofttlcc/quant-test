
import numpy as np
import pandas as pd
import logging
import pickle
import os
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import NotFittedError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MLPTrendModel:
    """
    MLP-based Trend Prediction Model.
    NOTE: Uses sklearn MLPClassifier, NOT LSTM (PyTorch unavailable).
    MINOR-004 FIX: 類名已從 LSTMTrendModel 改為 MLPTrendModel 以避免誤導。
    
    Structure: Input -> Hidden(64) -> Hidden(32) -> Output(1) [Sigmoid/ReLu]
    """
    def __init__(self, hidden_layer_sizes=(64, 32), learning_rate=0.001, max_iter=200):
        self.model = MLPClassifier(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver='adam',
            learning_rate_init=learning_rate,
            max_iter=max_iter,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, X, y):
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        
    def predict_proba(self, X):
        if not self.is_fitted:
            return np.zeros(len(X))
        X_scaled = self.scaler.transform(X)
        # Class 1 probability
        return self.model.predict_proba(X_scaled)[:, 1]

class MLPPredictor:
    # MINOR-001 FIX: 使用環境變數配置路徑
    def __init__(self, sequence_length=60, model_path=None):
        self.sequence_length = sequence_length
        self.model = MLPTrendModel()
        self.model_path = model_path or os.environ.get('ML_MODEL_PATH', 'temp/ml_models/mlp_model.pkl')
        
    def create_features(self, data: np.ndarray):
        """
        Create sliding window features.
        Since we use MLP, we flatten the sequence into a feature vector.
        Feature vector = [t-N, t-N+1, ..., t]
        
        CRITICAL-002 FIX: 使用當前收益（已實現）而非未來收益
        """
        xs, ys = [], []
        for i in range(len(data) - self.sequence_length - 1):
            x = data[i : i+self.sequence_length]  # Shape (seq_len,)
            
            # MAJOR-007 FIX: Normalize input window to handle price drift (Scale Invariant)
            # Convert raw prices to % change relative to window start
            if len(x) > 0 and x[0] != 0:
                x = (x / x[0]) - 1.0
            
            # CRITICAL-002 FIX: 目標是當前時點的收益方向（已實現）
            # 使用 data[i+seq_len] vs data[i+seq_len-1]，這是「當日」相對「昨日」
            target_val = data[i+self.sequence_length] - data[i+self.sequence_length-1]
            y = 1 if target_val > 0 else 0
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)

    def train(self, df: pd.DataFrame, save=True):
        """
        Train the model and optionally save it.
        """
        if 'Close' not in df.columns:
            logger.error("DataFrame missing 'Close' column.")
            return
        
        data = df['Close'].values
        # Note: We don't pre-normalize here, StandardScaler inside model does it.
        
        X, y = self.create_features(data)
        if len(X) == 0:
            logger.warning("Not enough data to create features.")
            return

        logger.info(f"Training MLP (Proxy for LSTM) on {len(X)} samples...")
        self.model.fit(X, y)
        logger.info("Training complete.")
        
        if save:
            self.save_model()
                
    def predict(self, sequence: np.ndarray) -> float:
        """
        Predict probability of Up move given a raw sequence.
        """
        # Ensure sequence is (1, seq_len)
        if sequence.ndim == 1:
            # Normalize (Same as create_features)
            if len(sequence) > 0 and sequence[0] != 0:
                sequence = (sequence / sequence[0]) - 1.0
            sequence = sequence.reshape(1, -1)
        else:
             # Batch normalization for 2D
             # Assuming shape (batch, seq_len)
             # Avoid in-place modification of original array if shared
             sequence = sequence.copy()
             for i in range(len(sequence)):
                 if sequence[i, 0] != 0:
                     sequence[i] = (sequence[i] / sequence[i, 0]) - 1.0
            
        prob = self.model.predict_proba(sequence)[0]
        return prob
        
    def save_model(self):
        """Save model to disk."""
        try:
            directory = os.path.dirname(self.model_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            
    def load_model(self):
        """Load model from disk."""
        if not os.path.exists(self.model_path):
            logger.warning(f"No model found at {self.model_path}")
            return False
            
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info(f"Model loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信號 (Issue 3 FIX: 策略接口適配)
        
        使 MLPPredictor 與 MomentumStrategy 等傳統策略接口相容，
        可在 StrategyArena 中使用。
        
        Args:
            df: 包含 OHLCV 數據的 DataFrame
            
        Returns:
            帶有 Signal 和 Position 列的 DataFrame
        """
        if df.empty or 'Close' not in df.columns:
            return df
            
        strat_df = df.copy()
        
        # 檢測是否為預訓練模型 (已加載)
        is_pretrained = self.model.is_fitted
        
        # 定義預測起始點
        # 如果是預訓練模型，則從序列長度後開始預測 (全量回測)
        # 如果是現場訓練，則保留前 80% 作為訓練集，只回測後 20%
        train_end = 0 if is_pretrained else int(len(strat_df) * 0.8)
        
        # 訓練模型（如果尚未訓練）
        if not is_pretrained and len(strat_df) > 50:
            # 只用訓練集數據訓練
            # Note: 重新計算 train_end 確保邏輯一致
            train_end = int(len(strat_df) * 0.8)
            train_df = strat_df.iloc[:train_end]
            self.train(train_df, save=False)
        
        # 如果模型已訓練 (包含剛訓練完的情況)，使用模型預測
        strat_df['Signal'] = 0
        strat_df['Position'] = 0.0
        
        if self.model.is_fitted and len(strat_df) > self.sequence_length:
            prices = strat_df['Close'].values
            
            # 確定預測範圍
            start_idx = max(self.sequence_length, train_end)
            
            # 對範圍內進行預測
            for i in range(start_idx, len(prices)):
                seq = prices[i-self.sequence_length:i]
                prob = self.predict(seq)
                
                # 概率 > 0.52 做多，< 0.48 做空/空倉
                if prob > 0.52:
                    strat_df.iloc[i, strat_df.columns.get_loc('Signal')] = 1
                elif prob < 0.48:
                    strat_df.iloc[i, strat_df.columns.get_loc('Signal')] = -1
            
            # Position: 持倉 (使用信號前向填充)
            strat_df['Position'] = strat_df['Signal'].replace(0, np.nan).ffill().fillna(0)
            strat_df['Position'] = strat_df['Position'].clip(0, 1)  # 只做多
            
            # 如果是非預訓練模型，訓練集區域強制為 0
            if not is_pretrained:
                strat_df.iloc[:train_end, strat_df.columns.get_loc('Position')] = 0
        else:
            # 未訓練時使用簡單動量策略作為後備 (Fallback)
            mom = strat_df['Close'].pct_change(10)
            strat_df.loc[mom > 0.02, 'Signal'] = 1
            strat_df['Position'] = (strat_df['Signal'] == 1).astype(float)
        
        return strat_df

# 向後兼容別名 (Backward Compatibility Aliases)
LSTMTrendModel = MLPTrendModel
LSTMPredictor = MLPPredictor

if __name__ == "__main__":
    print("--- SELF-TEST START: lstm_predictor.py (Persistence) ---")
    
    # Dummy Data (Sine Wave Trend)
    x = np.linspace(0, 100, 500)
    prices = 100 + np.sin(x) * 10
    df = pd.DataFrame({'Close': prices})
    
    path = "temp_test_model.pkl"
    predictor = LSTMPredictor(sequence_length=10, model_path=path)
    
    # Train & Save
    print("[TEST] Training & Saving...")
    predictor.train(df, save=True)
    
    # Load into new instance
    print("[TEST] Loading into new instance...")
    predictor2 = LSTMPredictor(sequence_length=10, model_path=path)
    loaded = predictor2.load_model()
    
    if loaded:
        print("[TEST] SUCCESS: Model loaded.")
        # Predict
        last_seq = prices[-10:]
        prob = predictor2.predict(last_seq)
        print(f"[TEST] Prediction from loaded model: {prob:.4f}")
    else:
        print("[TEST] FAILURE: Model load failed.")
        
    # Cleanup
    if os.path.exists(path):
        os.remove(path)
        
    print("--- SELF-TEST END ---")
