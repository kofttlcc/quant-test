import threading
import uuid
import logging
import traceback
import sys
import os
from datetime import datetime
import pandas as pd
import numpy as np
import time

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.model_registry import get_model_registry
from src.data_loader.downloader import fetch_data

logger = logging.getLogger(__name__)

class AITrainingJob:
    def __init__(self, job_id, model_type, params, ticker):
        self.job_id = job_id
        self.model_type = model_type
        self.params = params
        self.ticker = ticker
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0
        self.logs = []
        self.result = {}
        self.start_time = datetime.now()
        self.end_time = None
        self.error = None

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        logger.info(f"[Job {self.job_id}] {message}")

class AITrainer:
    """
    Manages background training jobs for AI models.
    """
    
    def __init__(self):
        self.jobs = {} # Dict[str, AITrainingJob]
        self.registry = get_model_registry()

    def start_training_job(self, model_type: str, ticker: str, params: dict) -> str:
        job_id = uuid.uuid4().hex
        job = AITrainingJob(job_id, model_type, params, ticker)
        self.jobs[job_id] = job
        
        # Start background thread
        thread = threading.Thread(target=self._run_training, args=(job,))
        thread.daemon = True # Allow exit if main process exits
        thread.start()
        
        return job_id

    def get_job_status(self, job_id: str) -> dict:
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "logs": job.logs[-10:], # Last 10 logs
            "result": job.result,
            "error": job.error,
            "duration": (datetime.now() - job.start_time).seconds if not job.end_time else (job.end_time - job.start_time).seconds
        }

    def _run_training(self, job: AITrainingJob):
        job.status = "running"
        job.log(f"Starting training for {job.model_type} on {job.ticker}")
        
        try:
            # 1. Fetch Data
            job.log("Fetching data...")
            df = fetch_data(job.ticker, start_date="2023-01-01")
            if df.empty:
                raise ValueError("No data fetched")
            job.progress = 10
            
            # 2. Initialize Model
            job.log("Initializing model...")
            model = None
            
            if job.model_type == 'lightgbm':
                from src.models.arena.tree_predictor import LightGBMPredictor, TreeModelConfig
                config = TreeModelConfig(
                    n_estimators=int(job.params.get('n_estimators', 100)),
                    max_depth=int(job.params.get('max_depth', 5)),
                    learning_rate=float(job.params.get('learning_rate', 0.05))
                )
                model = LightGBMPredictor(config)
                
            elif job.model_type == 'mlp':
                from src.models.arena.lstm_predictor import MLPPredictor
                from src.models.arena.lstm_predictor import MLPTrendModel
                
                lr = float(job.params.get('learning_rate', 0.001))
                n_estimators = int(job.params.get('n_estimators', 200))
                
                model = MLPPredictor()
                model.model = MLPTrendModel(hidden_layer_sizes=(64, 32), learning_rate=lr, max_iter=n_estimators)
            else:
                raise ValueError(f"Unknown model type: {job.model_type}")
                
            job.progress = 20
            
            # 3. Attach Callbacks & Train
            job.log("Training model with progress tracking...")
            
            # Callback Hooks
            def on_lgbm_epoch(epoch, logs):
                # LightGBM epoch is 0-indexed
                total_rounds = config.n_estimators
                progress = int((epoch / total_rounds) * 80) + 20 # 20% -> 100%
                job.progress = min(progress, 99)
                if epoch % 10 == 0:
                    job.log(f"Epoch {epoch}/{total_rounds}")

            def on_mlp_fold(fold, total_folds, score):
                # MLP Fold is 0-indexed
                progress = int(((fold + 1) / total_folds) * 80) + 20
                job.progress = min(progress, 99)
                job.log(f"CV Fold {fold+1}/{total_folds} - Acc: {score:.4f}")

            if job.model_type == 'lightgbm':
                model.on_epoch_end = on_lgbm_epoch
                model.generate_signals(df)
                
            elif job.model_type == 'mlp':
                model.on_fold_end = on_mlp_fold
                model.train(df, save=False)
               
            job.progress = 95
            
            # --- Phase 4: Compute Feature Importance ---
            feature_importance = {}
            try:
                job.log("Computing Feature Importance...")
                # Lazy import to avoid circular dependency issues if any
                from src.models.arena.feature_selector import FeatureSelector
                
                # Prepare Validation Data (using last 20%)
                split_idx = int(len(df) * 0.8)
                val_df = df.iloc[split_idx:].copy()
                
                if not val_df.empty:
                    # Target construction (Same as in training logic)
                    val_df['Target'] = val_df['Close'].shift(-1) > val_df['Close']
                    val_df = val_df.dropna()
                    
                    if not val_df.empty:
                        X_val = val_df.drop(columns=['Target', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume'], errors='ignore')
                        # Ensure only numeric
                        X_val = X_val.select_dtypes(include=[np.number])
                        y_val = val_df['Target'].astype(int)
                        
                        selector = FeatureSelector(model, n_repeats=3) # Low repeats for speed
                        # Note: 'model' wrapper needs to expose predict/score for permutation_importance
                        # Our wrappers (LightGBMPredictor, MLPPredictor) might need adaptation if they don't match sklearn exactly.
                        # LightGBMPredictor has 'predict_proba', MLPPredictor has 'predict'.
                        # Let's check compat or wrap it.
                        
                        # Wrapper for sklearn compatibility
                        class SklearnWrapper:
                            def __init__(self, predictor, model_type):
                                self.predictor = predictor
                                self.model_type = model_type
                                
                            def predict(self, X):
                                # Reconstruct df context if needed, but predictors usually take df.
                                # But FeatureSelector passes numpy or DF.
                                # Our predictors take DF and compute indicators internally? 
                                # Wait, LightGBM/MLP generate_signals/train take RAW DF.
                                # They compute features internally.
                                # Permutation importance shuffles columns of INPUT X.
                                # If input X is raw OHLCV, shuffling 'Close' breaks everything.
                                # WE CANNOT USE STANDARD PERMUTATION IMPORTANCE ON RAW OHLCV IF FEATURES ARE GEN'D INSID E.
                                # We must export features first.
                                
                                # For now, let's assume we can't easily do Permutation Importance on Raw Data pipelines 
                                # without refactoring the whole pipeline to separate FeatureGen from Model.
                                # Phase 3 implementation of FeatureSelector assumes X is Feature Matrix.
                                pass
                        
                        # Correct approach:
                        # LightGBM models usually have built-in feature importance.
                        if job.model_type == 'lightgbm' and hasattr(model.model, 'feature_importance'):
                            # Use native importance
                            imp = model.model.feature_importance()
                            names = model.model.feature_name()
                            # Normalise
                            total_gain = sum(imp)
                            if total_gain > 0:
                                feature_importance = {name: float(score/total_gain) for name, score in zip(names, imp)}
                                # Sort
                                feature_importance = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True)[:10])
                            
                        # MLP: No native importance. Leave empty for now or use Permutation if refactored.
                        # Given constraints, we skip MLP feature importance for this iteration to avoid breaking pipeline.
                        
            except Exception as fi_e:
                job.log(f"Warning: Feature Importance failed: {fi_e}")
            
            job.progress = 100
            job.log("Training complete. Saving model...")
            
            # 4. Save and Register
            version = self.registry.get_next_version(job.model_type)
            archive_path = self.registry.get_archive_path(job.model_type, version)
            
            # Save Archive
            # Assuming model has save_model(path) or we set model_path
            if hasattr(model, 'save_model'):
                # Quick hack for consistent API
                original_path = getattr(model, 'model_path', None)
                
                # Save to archive
                if job.model_type == 'mlp':
                    model.model_path = archive_path
                    model.save_model()
                    model.model_path = original_path # Restore
                elif job.model_type == 'lightgbm':
                    model.save_model(path=archive_path)
                    
            # Register
            self.registry.register_model(job.model_type, version, archive_path, job.params)
            
            job.result = {
                "version": version,
                "path": archive_path,
                "feature_importance": feature_importance
            }
            job.status = "completed"
            job.end_time = datetime.now()
            job.log(f"Job finished successfully. Version: {version}")
            
        except Exception as e:
            job.error = str(e)
            job.status = "failed"
            job.end_time = datetime.now()
            job.log(f"Training failed: {e}")
            logger.error(f"Job {job.job_id} failed: {traceback.format_exc()}")

# Global Instance
_trainer = None

def get_ai_trainer():
    global _trainer
    if _trainer is None:
        _trainer = AITrainer()
    return _trainer
