"""
tree_predictor.py - 樹模型預測器
=============================================
版本: v1.0 (專家優化建議 Sprint 2)
功能: LightGBM 替換 MLP，用於趨勢預測

專家建議:
- 樹模型訓練速度極快，適合滾動窗口重訓
- 提供特徵重要性，可解釋性高
- 小樣本表現優於深度學習

支持:
- LightGBM (優先)
- XGBoost (後備)
"""

import pandas as pd
import numpy as np
import logging
import pickle
import os
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 嘗試導入 LightGBM，若失敗則使用 XGBoost 或 sklearn
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    logger.warning("LightGBM not available, using fallback")

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler


@dataclass
class TreeModelConfig:
    """樹模型配置"""
    n_estimators: int = 100
    max_depth: int = 5
    learning_rate: float = 0.05
    min_child_samples: int = 20
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    reg_alpha: float = 0.1  # L1 正則化
    reg_lambda: float = 0.1  # L2 正則化
    early_stopping_rounds: int = 20
    verbose: int = -1


class LightGBMPredictor:
    """
    LightGBM 趨勢預測器
    
    專家建議:
    - 訓練速度快，適合 Walk-Forward 重訓
    - 正則化防止過擬合
    - 特徵重要性可解釋
    """
    
    def __init__(self, config: TreeModelConfig = None):
        self.config = config or TreeModelConfig()
        self.model = None
        self.feature_names: List[str] = []
        self.is_fitted = False
        self.model_path = os.environ.get('TREE_MODEL_PATH', 'temp/ml_models/lgbm_model.pkl')
        
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None):
        """
        訓練模型
        
        Args:
            X: 特徵矩陣 (n_samples, n_features)
            y: 目標標籤 (0/1 二分類或連續值)
        """
        self.feature_names = feature_names or [f"f{i}" for i in range(X.shape[1])]
        
        # 確定任務類型
        unique_y = np.unique(y)
        is_classification = len(unique_y) <= 10
        
        if HAS_LIGHTGBM:
            self._fit_lightgbm(X, y, is_classification)
        elif HAS_XGBOOST:
            self._fit_xgboost(X, y, is_classification)
        else:
            self._fit_sklearn(X, y, is_classification)
            
        self.is_fitted = True
        logger.info(f"TreePredictor fitted on {X.shape[0]} samples, {X.shape[1]} features")
    
    def _fit_lightgbm(self, X: np.ndarray, y: np.ndarray, is_classification: bool):
        """使用 LightGBM 訓練"""
        params = {
            'objective': 'binary' if is_classification else 'regression',
            'metric': 'binary_logloss' if is_classification else 'mse',
            'boosting_type': 'gbdt',
            'num_leaves': 2 ** self.config.max_depth - 1,
            'max_depth': self.config.max_depth,
            'learning_rate': self.config.learning_rate,
            'min_child_samples': self.config.min_child_samples,
            'subsample': self.config.subsample,
            'colsample_bytree': self.config.colsample_bytree,
            'reg_alpha': self.config.reg_alpha,
            'reg_lambda': self.config.reg_lambda,
            'verbose': self.config.verbose,
            'seed': 42
        }
        
        # 創建數據集
        train_data = lgb.Dataset(X, label=y, feature_name=self.feature_names)
        
        # 訓練
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=self.config.n_estimators,
        )
        
    def _fit_xgboost(self, X: np.ndarray, y: np.ndarray, is_classification: bool):
        """使用 XGBoost 訓練"""
        params = {
            'objective': 'binary:logistic' if is_classification else 'reg:squarederror',
            'max_depth': self.config.max_depth,
            'learning_rate': self.config.learning_rate,
            'subsample': self.config.subsample,
            'colsample_bytree': self.config.colsample_bytree,
            'reg_alpha': self.config.reg_alpha,
            'reg_lambda': self.config.reg_lambda,
            'seed': 42
        }
        
        dtrain = xgb.DMatrix(X, label=y, feature_names=self.feature_names)
        self.model = xgb.train(params, dtrain, num_boost_round=self.config.n_estimators)
        
    def _fit_sklearn(self, X: np.ndarray, y: np.ndarray, is_classification: bool):
        """使用 sklearn GradientBoosting 作為後備"""
        if is_classification:
            self.model = GradientBoostingClassifier(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                learning_rate=self.config.learning_rate,
                min_samples_leaf=self.config.min_child_samples,
                subsample=self.config.subsample,
                random_state=42
            )
        else:
            from sklearn.ensemble import GradientBoostingRegressor
            self.model = GradientBoostingRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                learning_rate=self.config.learning_rate,
                min_samples_leaf=self.config.min_child_samples,
                subsample=self.config.subsample,
                random_state=42
            )
        self.model.fit(X, y)
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """預測"""
        if not self.is_fitted:
            return np.zeros(len(X))
            
        if HAS_LIGHTGBM and isinstance(self.model, lgb.Booster):
            return self.model.predict(X)
        elif HAS_XGBOOST and hasattr(self.model, 'predict'):
            dtest = xgb.DMatrix(X, feature_names=self.feature_names)
            return self.model.predict(dtest)
        else:
            if hasattr(self.model, 'predict_proba'):
                return self.model.predict_proba(X)[:, 1]
            return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """預測概率（分類任務）"""
        return self.predict(X)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        獲取特徵重要性
        
        專家建議: 用於檢測是否過度依賴單一特徵（如 Beta）
        """
        if not self.is_fitted:
            return {}
            
        if HAS_LIGHTGBM and isinstance(self.model, lgb.Booster):
            importance = self.model.feature_importance(importance_type='gain')
        elif HAS_XGBOOST and hasattr(self.model, 'get_score'):
            score = self.model.get_score(importance_type='gain')
            importance = [score.get(f, 0) for f in self.feature_names]
        else:
            importance = getattr(self.model, 'feature_importances_', np.zeros(len(self.feature_names)))
        
        # 歸一化
        total = sum(importance) + 1e-8
        return {name: imp / total for name, imp in zip(self.feature_names, importance)}
    
    def save_model(self, path: str = None):
        """保存模型"""
        path = path or self.model_path
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'feature_names': self.feature_names,
                    'config': self.config
                }, f)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    def load_model(self, path: str = None) -> bool:
        """加載模型"""
        path = path or self.model_path
        if not os.path.exists(path):
            return False
            
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']
            self.config = data['config']
            self.is_fitted = True
            logger.info(f"Model loaded from {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信號 (Issue 3 FIX: 策略接口適配)
        
        使 LightGBMPredictor 與 MomentumStrategy 等傳統策略接口相容，
        可在 StrategyArena 中使用。
        
        Args:
            df: 包含 OHLCV 數據的 DataFrame
            
        Returns:
            帶有 Signal 和 Position 列的 DataFrame
        """
        if df.empty or 'Close' not in df.columns:
            return df
            
        strat_df = df.copy()
        
        # 創建特徵
        strat_df['Returns'] = strat_df['Close'].pct_change()
        strat_df['SMA_5'] = strat_df['Close'].rolling(5).mean()
        strat_df['SMA_20'] = strat_df['Close'].rolling(20).mean()
        strat_df['Volatility'] = strat_df['Returns'].rolling(20).std()
        strat_df['Momentum'] = strat_df['Close'].pct_change(10)
        
        # RSI
        delta = strat_df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / (loss + 1e-8)
        strat_df['RSI'] = 100 - (100 / (1 + rs))
        strat_df['RSI_norm'] = (strat_df['RSI'] - 50) / 50  # 歸一化到 [-1, 1]
        
        # 填充 NaN
        strat_df = strat_df.fillna(0)
        
        # 特徵列
        feature_cols = ['Returns', 'SMA_5', 'SMA_20', 'Volatility', 'Momentum', 'RSI_norm']
        
        # 記錄訓練集結束位置
        # 檢測是否為預訓練模型 (已加載)
        is_pretrained = self.is_fitted
        
        # 定義預測起始點
        # 如果是預訓練模型，則從頭(或有特徵處)開始預測
        # 如果是現場訓練，則保留前 80% 作為訓練集，只回測後 20%
        train_end = 0 if is_pretrained else int(len(strat_df) * 0.8)
        
        # CRITICAL-002 FIX: 訓練模型 (如果尚未訓練)
        # 修正 Look-ahead Bias：使用當日收益率（已實現）作為標籤，而非未來收益
        if not is_pretrained and len(strat_df) > 50:
            train_end = int(len(strat_df) * 0.8) # Ensure fallback training uses split
            
            # 創建目標變量: 使用當日收益率（今天相比昨天）
            # 這是「已實現」的收益，不涉及未來數據
            # 模型學習：基於 T-1 的特徵預測 T 的方向
            daily_returns = strat_df['Close'].pct_change()
            y = (daily_returns > 0).astype(int).values
            X = strat_df[feature_cols].values
            
            # 時移：確保特徵在標籤之前
            # X[t] 預測 y[t+1]，因此訓練時使用 X[:-1] 和 y[1:]
            X_train = X[:-1]
            y_train = y[1:]
            
            # 只用訓練集數據 (80%)
            train_cutoff = min(train_end, len(X_train))
            if train_cutoff > 30:
                self.fit(X_train[:train_cutoff], y_train[:train_cutoff], feature_names=feature_cols)
                logger.info(f"CRITICAL-002 FIX: Model trained with look-ahead bias prevention. Train size: {train_cutoff}")
        
        # 預測 - CRITICAL FIX: 只對測試集預測，避免訓練測試洩漏
        strat_df['Signal'] = 0
        strat_df['Position'] = 0.0
        
        if self.is_fitted:
            X_all = strat_df[feature_cols].values
            
            # 確定預測範圍
            # 對於預訓練模型，從特徵可用的位置開始 (例如 SMA_20 需要 20 個點)
            start_idx = train_end if not is_pretrained else 20
            start_idx = max(start_idx, 0)
            
            if start_idx < len(X_all):
                X_test = X_all[start_idx:]
                predictions_test = self.predict(X_test)
                
                # 將預測概率轉為信號: >0.55 做多, <0.45 做空/空倉
                test_signals = np.zeros(len(predictions_test))
                test_signals[predictions_test > 0.55] = 1
                test_signals[predictions_test < 0.45] = -1
                
                # 賦值到測試集區域
                strat_df.iloc[start_idx:, strat_df.columns.get_loc('Signal')] = test_signals
            
            # Position: 持倉 (使用信號前向填充)
            strat_df['Position'] = strat_df['Signal'].replace(0, np.nan).ffill().fillna(0)
            strat_df['Position'] = strat_df['Position'].clip(0, 1)  # 只做多
            
            # 如果是非預訓練模型，訓練集區域強制為 0
            if not is_pretrained:
                strat_df.iloc[:train_end, strat_df.columns.get_loc('Position')] = 0
        else:
            # 未訓練時使用簡單動量策略作為後備
            strat_df.loc[strat_df['Momentum'] > 0.02, 'Signal'] = 1
            strat_df['Position'] = (strat_df['Signal'] == 1).astype(float)
        
        return strat_df


class FeatureNeutralizer:
    """
    特徵中性化器
    
    專家建議: 防止過擬合的殺手鐧
    確保模型不是僅僅在做多高貝塔（High Beta）的股票，
    而是在尋找真正的超額收益
    
    方法: 回歸中性化
    Alpha_Neutralized = Alpha - Beta * Factor
    """
    
    def __init__(self):
        self.neutralization_models: Dict[str, any] = {}
        
    def neutralize(
        self, 
        alpha: pd.Series, 
        factors: pd.DataFrame,
        method: str = 'regression'
    ) -> pd.Series:
        """
        對 Alpha 信號進行因子中性化
        
        Args:
            alpha: 原始 Alpha 信號
            factors: 需要中性化的因子 (如 Beta, Size 等)
            method: 中性化方法 ('regression' 或 'rank')
            
        Returns:
            中性化後的 Alpha 信號
        """
        if method == 'regression':
            return self._neutralize_regression(alpha, factors)
        elif method == 'rank':
            return self._neutralize_rank(alpha, factors)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _neutralize_regression(self, alpha: pd.Series, factors: pd.DataFrame) -> pd.Series:
        """
        回歸中性化
        
        Alpha_neutral = Alpha - sum(beta_i * Factor_i)
        """
        from sklearn.linear_model import LinearRegression
        
        # 對齊數據
        aligned = pd.concat([alpha, factors], axis=1).dropna()
        if len(aligned) < 10:
            return alpha
            
        y = aligned.iloc[:, 0].values
        X = aligned.iloc[:, 1:].values
        
        # 擬合
        lr = LinearRegression()
        lr.fit(X, y)
        
        # 計算殘差
        predicted = lr.predict(X)
        residual = y - predicted
        
        # 重建 Series
        result = pd.Series(residual, index=aligned.index, name=f"{alpha.name}_neutral")
        return result.reindex(alpha.index)
    
    def _neutralize_rank(self, alpha: pd.Series, factors: pd.DataFrame) -> pd.Series:
        """
        排名中性化（更穩健）
        
        在每個因子分位數內進行 Z-score 標準化
        """
        # 對因子進行分桶
        n_buckets = 5
        factor_rank = factors.iloc[:, 0].rank(pct=True)
        buckets = pd.cut(factor_rank, bins=n_buckets, labels=False)
        
        # 在每個桶內標準化 Alpha
        result = alpha.copy()
        for bucket in range(n_buckets):
            mask = buckets == bucket
            if mask.sum() > 1:
                bucket_alpha = alpha[mask]
                z_score = (bucket_alpha - bucket_alpha.mean()) / (bucket_alpha.std() + 1e-8)
                result[mask] = z_score
                
        return result
    
    def check_exposure(self, alpha: pd.Series, factor: pd.Series) -> float:
        """
        檢查 Alpha 對因子的暴露度
        
        Returns:
            相關係數 (越接近 0 越中性)
        """
        aligned = pd.concat([alpha, factor], axis=1).dropna()
        if len(aligned) < 10:
            return 0.0
        return aligned.iloc[:, 0].corr(aligned.iloc[:, 1])


# 向後兼容別名
TreePredictor = LightGBMPredictor


if __name__ == "__main__":
    print("--- SELF-TEST: tree_predictor.py ---")
    print(f"LightGBM available: {HAS_LIGHTGBM}")
    print(f"XGBoost available: {HAS_XGBOOST}")
    
    # 創建模擬數據
    np.random.seed(42)
    n_samples = 500
    n_features = 10
    
    X = np.random.randn(n_samples, n_features)
    # 目標: 前兩個特徵的線性組合 + 噪聲
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    
    print(f"\n[TEST] Training data: {X.shape}")
    
    # 測試預測器
    predictor = LightGBMPredictor()
    predictor.fit(X, y, feature_names=[f"feature_{i}" for i in range(n_features)])
    
    # 預測
    preds = predictor.predict(X[:10])
    print(f"\n[TEST] Predictions (first 10): {preds}")
    
    # 特徵重要性
    importance = predictor.get_feature_importance()
    print("\n[TEST] Feature Importance (top 5):")
    sorted_imp = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for name, imp in sorted_imp[:5]:
        print(f"  {name}: {imp:.3f}")
    
    # 測試中性化器
    print("\n[TEST] Feature Neutralization:")
    alpha = pd.Series(np.random.randn(100), name="alpha")
    beta = pd.Series(np.random.randn(100) * 0.5 + alpha * 0.3, name="beta")  # 與 alpha 相關
    
    neutralizer = FeatureNeutralizer()
    
    # 中性化前的暴露
    exposure_before = neutralizer.check_exposure(alpha, beta)
    print(f"  Exposure before: {exposure_before:.3f}")
    
    # 中性化
    factors = pd.DataFrame({"beta": beta})
    alpha_neutral = neutralizer.neutralize(alpha, factors)
    
    # 中性化後的暴露
    exposure_after = neutralizer.check_exposure(alpha_neutral, beta)
    print(f"  Exposure after: {exposure_after:.3f}")
    
    print("\n--- SELF-TEST COMPLETE ---")
