import unittest
import sys
import os
import json
import time
import threading
import shutil
from flask import Flask

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.backend.api_server import app
from src.services.model_registry import ModelRegistry

class TestV2Integration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Setup Test Client
        cls.client = app.test_client()
        cls.headers = {'X-API-Key': 'test_key'} # Assuming test key logic or bypass in dev
        
        # Override Registry Path for Test
        cls.test_dir = "tests/temp_v2_data"
        ModelRegistry.REGISTRY_PATH = f"{cls.test_dir}/registry.json"
        ModelRegistry.MODELS_DIR = f"{cls.test_dir}/archive"
        os.makedirs(cls.test_dir, exist_ok=True)
        
    @classmethod
    def tearDownClass(cls):
        # Cleanup
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
            
    def test_01_train_model(self):
        """Test launching an async training job"""
        payload = {
            "model_type": "mlp",
            "ticker": "BTC-USD",
            "params": {
                "n_estimators": 10,
                "learning_rate": 0.01
            }
        }
        res = self.client.post('/api/v1/model/train', json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('job_id', data)
        self.__class__.job_id = data['job_id']
        print(f"\nCreated Job ID: {self.job_id}")

    def test_02_poll_status(self):
        """Poll status until complete"""
        if not hasattr(self.__class__, 'job_id'):
            self.skipTest("No job_id from previous test")
            
        max_retries = 30
        completed = False
        
        for i in range(max_retries):
            res = self.client.get(f'/api/v1/model/train/status/{self.job_id}', headers=self.headers)
            self.assertEqual(res.status_code, 200)
            data = res.get_json()
            
            print(f"Status poll {i}: {data['status']} - Progress: {data['progress']}%")
            
            if data['status'] == 'completed':
                completed = True
                break
            elif data['status'] == 'failed':
                self.fail(f"Training failed: {data.get('error')}")
                
            time.sleep(1)
            
        self.assertTrue(completed, "Training timed out")

    def test_03_list_models(self):
        """Verify model is registered"""
        res = self.client.get('/api/v1/models?type=mlp', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('models', data)
        self.assertTrue(len(data['models']) > 0)
        print(f"Found {len(data['models'])} MLP models")

    def test_04_predict(self):
        """Test inference endpoint"""
        payload = {
            "ticker": "BTC-USD",
            "model_type": "mlp"
        }
        res = self.client.post('/api/v1/model/predict', json=payload, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        
        self.assertIn('signal', data)
        self.assertIn('probability', data)
        print(f"Prediction: {data['signal']} ({data['probability']})")

if __name__ == '__main__':
    unittest.main()
