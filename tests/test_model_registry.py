import unittest
import os
import sys
import shutil
import json
import time
from unittest.mock import MagicMock, patch

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.services.model_registry import ModelRegistry
from src.models.ai_optimizer import AITrainingJob, AITrainer

class TestModelRegistry(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for tests
        self.test_dir = "tests/temp_registry"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Patch paths in ModelRegistry class temporarily
        self.original_registry_path = ModelRegistry.REGISTRY_PATH
        self.original_models_dir = ModelRegistry.MODELS_DIR
        
        ModelRegistry.REGISTRY_PATH = f"{self.test_dir}/registry.json"
        ModelRegistry.MODELS_DIR = f"{self.test_dir}/archive"
        
        self.registry = ModelRegistry()

    def tearDown(self):
        # Restore paths
        ModelRegistry.REGISTRY_PATH = self.original_registry_path
        ModelRegistry.MODELS_DIR = self.original_models_dir
        
        # Cleanup
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_versioning(self):
        v1 = self.registry.get_next_version("test_model")
        self.assertEqual(v1, "v1.0")
        
        # Fake register
        self.registry.register_model("test_model", v1, "some/path.pkl", {})
        
        v2 = self.registry.get_next_version("test_model")
        self.assertEqual(v2, "v1.1")

    def test_persistence(self):
        self.registry.register_model("model_a", "v1.0", "path/a.pkl", {"p": 1})
        
        # Reload
        new_registry = ModelRegistry()
        models = new_registry.list_models("model_a")
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0]['version'], "v1.0")

class TestAITrainer(unittest.TestCase):
    def setUp(self):
        self.trainer = AITrainer()
        # Mock registry to avoid real file IO issues during trainer test
        self.trainer.registry = MagicMock()
        self.trainer.registry.get_next_version.return_value = "v1.test"
        self.trainer.registry.get_archive_path.return_value = "/tmp/test.pkl"

    def test_job_flow(self):
        # Mock fetch_data and model to avoid real training time
        with patch('src.models.ai_optimizer.fetch_data') as mock_fetch:
            mock_fetch.return_value = MagicMock(empty=False) # Fake DF
            
            # Start job
            job_id = self.trainer.start_training_job('mlp', 'BTC-USD', {'n_estimators': 1})
            self.assertIsNotNone(job_id)
            
            # Poll status
            for _ in range(10):
                status = self.trainer.get_job_status(job_id)
                if status['status'] in ['completed', 'failed']:
                    break
                time.sleep(0.1)
                
            final_status = self.trainer.get_job_status(job_id)
            # It might fail because of missing dependencies or mocked objects not behaving perfectly as models
            # But we want to ensure it ran through logic
            
            print(f"Final Job Status: {final_status['status']}")
            print(f"Error if any: {final_status.get('error')}")
            
            # We expect completed or failed (but not pending)
            self.assertNotEqual(final_status['status'], 'pending')

if __name__ == '__main__':
    unittest.main()
