"""
walk_forward.py - Walk-Forward 驗證器
=============================================
版本: v1.0 (專家優化建議 Sprint 1)
功能: 嚴格的滾動窗口訓練/測試分割

專家建議架構:
- 訓練窗口: 2 年 (504 交易日)
- 測試窗口: 3 個月 (63 交易日)
- 滑動步長: 3 個月 (63 交易日)
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Tuple, Generator, Dict, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WalkForwardFold:
    """單個 Walk-Forward 折疊"""
    fold_id: int
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    train_slice: slice
    test_slice: slice


@dataclass
class WalkForwardResult:
    """Walk-Forward 驗證結果"""
    fold_id: int
    train_sharpe: float
    test_sharpe: float
    train_return: float
    test_return: float
    predictions: np.ndarray
    actuals: np.ndarray


class WalkForwardValidator:
    """
    Walk-Forward 驗證器
    
    專家建議:
    - 不要用 2008-2020 訓練，2021-2026 測試（忽視市場風格切換）
    - 正確做法：訓練 2 年，預測 3 個月；然後窗口滑動 3 個月，重新訓練
    
    架構:
    |---Train (2Y)---||---Test (3M)---|
                     |---Train (2Y)---||---Test (3M)---|
                                      |---Train (2Y)---||---Test (3M)---|
    """
    
    def __init__(
        self, 
        train_years: float = 2.0, 
        test_months: int = 3, 
        step_months: int = 3
    ):
        """
        初始化驗證器
        
        Args:
            train_years: 訓練窗口年數 (默認 2 年)
            test_months: 測試窗口月數 (默認 3 個月)
            step_months: 滑動步長月數 (默認 3 個月)
        """
        self.train_days = int(train_years * 252)  # 交易日
        self.test_days = test_months * 21         # 約 21 交易日/月
        self.step_days = step_months * 21
        
        logger.info(
            f"WalkForwardValidator initialized: "
            f"Train={self.train_days}d, Test={self.test_days}d, Step={self.step_days}d"
        )
    
    def generate_folds(self, data: pd.DataFrame) -> List[WalkForwardFold]:
        """
        生成所有 Walk-Forward 折疊
        
        Args:
            data: 帶有 DatetimeIndex 的 DataFrame
            
        Returns:
            WalkForwardFold 列表
        """
        n = len(data)
        min_required = self.train_days + self.test_days
        
        if n < min_required:
            logger.warning(
                f"Data length ({n}) < minimum required ({min_required}). "
                f"No folds generated."
            )
            return []
        
        folds = []
        fold_id = 0
        start_idx = 0
        
        while start_idx + self.train_days + self.test_days <= n:
            train_start_idx = start_idx
            train_end_idx = start_idx + self.train_days
            test_start_idx = train_end_idx
            test_end_idx = min(test_start_idx + self.test_days, n)
            
            fold = WalkForwardFold(
                fold_id=fold_id,
                train_start=data.index[train_start_idx],
                train_end=data.index[train_end_idx - 1],
                test_start=data.index[test_start_idx],
                test_end=data.index[test_end_idx - 1],
                train_slice=slice(train_start_idx, train_end_idx),
                test_slice=slice(test_start_idx, test_end_idx)
            )
            
            folds.append(fold)
            fold_id += 1
            start_idx += self.step_days
        
        logger.info(f"Generated {len(folds)} walk-forward folds")
        return folds
    
    def split(self, data: pd.DataFrame) -> Generator[Tuple[pd.DataFrame, pd.DataFrame, int], None, None]:
        """
        生成訓練/測試分割的生成器
        
        Yields:
            (train_df, test_df, fold_id)
        """
        folds = self.generate_folds(data)
        
        for fold in folds:
            train_df = data.iloc[fold.train_slice].copy()
            test_df = data.iloc[fold.test_slice].copy()
            yield train_df, test_df, fold.fold_id
    
    def validate_model(
        self, 
        data: pd.DataFrame, 
        model_factory,  # Callable that returns a fresh model
        feature_cols: List[str],
        target_col: str,
        metric_fn=None  # Optional custom metric function
    ) -> List[WalkForwardResult]:
        """
        執行完整的 Walk-Forward 驗證
        
        Args:
            data: 完整數據集
            model_factory: 返回新模型實例的工廠函數
            feature_cols: 特徵列名
            target_col: 目標列名
            metric_fn: 自定義指標函數 (predictions, actuals) -> float
            
        Returns:
            每個折疊的驗證結果列表
        """
        results = []
        
        for train_df, test_df, fold_id in self.split(data):
            logger.info(f"Processing fold {fold_id}...")
            
            # 提取特徵和目標
            X_train = train_df[feature_cols].values
            y_train = train_df[target_col].values
            X_test = test_df[feature_cols].values
            y_test = test_df[target_col].values
            
            # 處理 NaN
            train_mask = ~np.isnan(X_train).any(axis=1) & ~np.isnan(y_train)
            test_mask = ~np.isnan(X_test).any(axis=1) & ~np.isnan(y_test)
            
            X_train_clean = X_train[train_mask]
            y_train_clean = y_train[train_mask]
            X_test_clean = X_test[test_mask]
            y_test_clean = y_test[test_mask]
            
            if len(X_train_clean) < 50 or len(X_test_clean) < 10:
                logger.warning(f"Fold {fold_id}: Insufficient data, skipping")
                continue
            
            # 訓練模型
            model = model_factory()
            model.fit(X_train_clean, y_train_clean)
            
            # 預測
            train_pred = model.predict(X_train_clean)
            test_pred = model.predict(X_test_clean)
            
            # 計算指標
            if metric_fn:
                train_metric = metric_fn(train_pred, y_train_clean)
                test_metric = metric_fn(test_pred, y_test_clean)
            else:
                # 默認: 計算 Sharpe-like 指標
                train_metric = self._calculate_sharpe(train_pred, y_train_clean)
                test_metric = self._calculate_sharpe(test_pred, y_test_clean)
            
            # 計算回報
            train_return = np.mean(train_pred * y_train_clean) * 252
            test_return = np.mean(test_pred * y_test_clean) * 252
            
            result = WalkForwardResult(
                fold_id=fold_id,
                train_sharpe=train_metric,
                test_sharpe=test_metric,
                train_return=train_return,
                test_return=test_return,
                predictions=test_pred,
                actuals=y_test_clean
            )
            
            # [LOW-002] 擴展指標打印
            metrics_extended = self._calculate_metrics(test_pred, y_test_clean)
            
            results.append(result)
            logger.info(
                f"  Fold {fold_id}: Train Sharpe={train_metric:.2f}, "
                f"Test Sharpe={test_metric:.2f}, Test WR={metrics_extended['Win_Rate']:.1%}"
            )
        
        return results
    
    def _calculate_metrics(self, predictions: np.ndarray, actuals: np.ndarray) -> Dict[str, float]:
        """
        [LOW-002] 計算更全面的策略指標
        
        Returns:
            Dict: {Sharpe, Win_Rate, Profit_Factor, ...}
        """
        strategy_returns = predictions * actuals
        if len(strategy_returns) < 2:
             return {"Sharpe": 0.0, "Win_Rate": 0.0, "Profit_Factor": 0.0}
        
        # 1. Sharpe
        mean_ret = np.mean(strategy_returns)
        std_ret = np.std(strategy_returns)
        sharpe = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 1e-8 else 0.0
        
        # 2. Win Rate
        wins = strategy_returns > 0
        win_rate = np.mean(wins)
        
        # 3. Profit Factor
        gross_profit = np.sum(strategy_returns[strategy_returns > 0])
        gross_loss = np.abs(np.sum(strategy_returns[strategy_returns < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf
        
        return {
            "Sharpe": sharpe,
            "Win_Rate": win_rate,
            "Profit_Factor": profit_factor
        }

    def _calculate_sharpe(self, predictions: np.ndarray, actuals: np.ndarray) -> float:
        """保留舊方法兼容性 (Deprecated)"""
        return self._calculate_metrics(predictions, actuals)["Sharpe"]
    
    def get_aggregate_metrics(self, results: List[WalkForwardResult]) -> Dict[str, float]:
        """獲取聚合指標"""
        if not results:
            return {}
            
        train_sharpes = [r.train_sharpe for r in results]
        test_sharpes = [r.test_sharpe for r in results]
        train_returns = [r.train_return for r in results]
        test_returns = [r.test_return for r in results]
        
        # 計算過擬合比率
        # 如果 Test/Train < 0.7，說明嚴重過擬合
        avg_train = np.mean(train_sharpes)
        avg_test = np.mean(test_sharpes)
        overfit_ratio = avg_test / avg_train if avg_train > 0 else 0
        
        return {
            "n_folds": len(results),
            "avg_train_sharpe": avg_train,
            "avg_test_sharpe": avg_test,
            "std_test_sharpe": np.std(test_sharpes),
            "overfit_ratio": overfit_ratio,
            "avg_train_return": np.mean(train_returns),
            "avg_test_return": np.mean(test_returns),
            "hit_rate": np.mean([1 if r.test_sharpe > 0 else 0 for r in results])
        }


class PurgedWalkForwardValidator(WalkForwardValidator):
    """
    帶有 Purging 和 Embargo 的 Walk-Forward 驗證器
    
    進階技術:
    - Purging: 移除訓練集末端可能洩漏信息的數據
    - Embargo: 測試集開頭留出緩衝區
    
    防止信息洩漏導致的過擬合
    """
    
    def __init__(
        self, 
        train_years: float = 2.0, 
        test_months: int = 3, 
        step_months: int = 3,
        purge_days: int = 5,
        embargo_days: int = 5
    ):
        super().__init__(train_years, test_months, step_months)
        self.purge_days = purge_days
        self.embargo_days = embargo_days
        
    def generate_folds(self, data: pd.DataFrame) -> List[WalkForwardFold]:
        """生成帶有 Purging 的折疊"""
        base_folds = super().generate_folds(data)
        
        purged_folds = []
        for fold in base_folds:
            # 調整訓練集結束位置 (Purge)
            new_train_end = fold.train_slice.stop - self.purge_days
            
            # 調整測試集開始位置 (Embargo)
            new_test_start = fold.test_slice.start + self.embargo_days
            
            if new_train_end <= fold.train_slice.start or new_test_start >= fold.test_slice.stop:
                continue
                
            purged_fold = WalkForwardFold(
                fold_id=fold.fold_id,
                train_start=fold.train_start,
                train_end=data.index[new_train_end - 1],
                test_start=data.index[new_test_start],
                test_end=fold.test_end,
                train_slice=slice(fold.train_slice.start, new_train_end),
                test_slice=slice(new_test_start, fold.test_slice.stop)
            )
            purged_folds.append(purged_fold)
        
        return purged_folds


if __name__ == "__main__":
    print("--- SELF-TEST: walk_forward.py ---")
    
    # 創建模擬數據
    np.random.seed(42)
    dates = pd.date_range("2018-01-01", "2026-01-01", freq="B")
    n = len(dates)
    
    data = pd.DataFrame({
        "Close": 100 * np.exp(np.cumsum(np.random.normal(0.0003, 0.01, n))),
        "Feature1": np.random.randn(n),
        "Feature2": np.random.randn(n),
    }, index=dates)
    
    data["Target"] = data["Close"].pct_change().shift(-1)  # 次日收益作為目標
    data = data.dropna()
    
    print(f"\n[TEST] Data shape: {data.shape}")
    print(f"[TEST] Date range: {data.index[0]} to {data.index[-1]}")
    
    # 測試基本驗證器
    print("\n[TEST] Basic WalkForwardValidator:")
    validator = WalkForwardValidator(train_years=2, test_months=3, step_months=3)
    folds = validator.generate_folds(data)
    print(f"  Generated {len(folds)} folds")
    
    if folds:
        print(f"  First fold: Train {folds[0].train_start} to {folds[0].train_end}")
        print(f"              Test  {folds[0].test_start} to {folds[0].test_end}")
        print(f"  Last fold:  Train {folds[-1].train_start} to {folds[-1].train_end}")
        print(f"              Test  {folds[-1].test_start} to {folds[-1].test_end}")
    
    # 測試 Purged 驗證器
    print("\n[TEST] PurgedWalkForwardValidator:")
    purged_validator = PurgedWalkForwardValidator(
        train_years=2, test_months=3, step_months=3,
        purge_days=5, embargo_days=5
    )
    purged_folds = purged_validator.generate_folds(data)
    print(f"  Generated {len(purged_folds)} purged folds")
    
    # 測試完整驗證流程 (使用簡單線性模型)
    print("\n[TEST] Full validation with dummy model:")
    from sklearn.linear_model import Ridge
    
    def model_factory():
        return Ridge(alpha=1.0)
    
    results = validator.validate_model(
        data, 
        model_factory, 
        feature_cols=["Feature1", "Feature2"],
        target_col="Target"
    )
    
    if results:
        metrics = validator.get_aggregate_metrics(results)
        print(f"\n  Aggregate Metrics:")
        print(f"    Folds: {metrics['n_folds']}")
        print(f"    Avg Train Sharpe: {metrics['avg_train_sharpe']:.2f}")
        print(f"    Avg Test Sharpe: {metrics['avg_test_sharpe']:.2f}")
        print(f"    Overfit Ratio: {metrics['overfit_ratio']:.2f}")
        print(f"    Hit Rate: {metrics['hit_rate']:.1%}")
    
    print("\n--- SELF-TEST COMPLETE ---")
