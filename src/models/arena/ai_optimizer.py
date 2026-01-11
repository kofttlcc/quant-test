import threading
import uuid
import logging
import traceback
import sys
import os
from datetime import datetime
import pandas as pd
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
            
            # 3. Simulate Training Loop for Visualization (or hook into real training)
            # Since actual sklearn/lgbm fit is blocking, we can't easily get real-time progress 
            # without custom callbacks. For now, we simulate progress steps around the blocking call.
            
            job.log("Fitting model (this may take a while)...")
            
            # TODO: Add real callbacks to models later.
            # For now, just call generate_signals or train
            if job.model_type == 'lightgbm':
               # LightGBM training is fast usually
               model.generate_signals(df)
            elif job.model_type == 'mlp':
               model.train(df, save=False)
               
            job.progress = 90
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
                "path": archive_path
            }
            job.progress = 100
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
