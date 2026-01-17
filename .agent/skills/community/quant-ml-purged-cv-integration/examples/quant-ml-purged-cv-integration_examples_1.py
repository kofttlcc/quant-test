from src.models.validation import CombinatorialPurgedKFold
from sklearn.base import clone

class MLModel:
    def fit_cv(self, X, y):
        # 1. 標準化
        X_scaled = self.scaler.fit_transform(X)
        
        # 2. Purged CV 循環
        cv = CombinatorialPurgedKFold(
            n_splits=5, 
            n_test_splits=1, 
            purge_window=5  # 依據標籤前視長度設定
        )
        
        best_score = -np.inf
        
        for train_idx, val_idx in cv.split(X_scaled):
            fold_model = clone(self.base_model)
            fold_model.fit(X_scaled[train_idx], y[train_idx])
            
            score = fold_model.score(X_scaled[val_idx], y[val_idx])
            
            if score > best_score:
                best_score = score
                self.best_model = fold_model
        
        self.model = self.best_model
