import unittest
import sys
import os
import shutil
import json
from unittest.mock import MagicMock, patch

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Mock modules before importing api_server if needed, but integration test uses API client usually.
# Here we want to unit test the run_backtest logic specifically or integration test it.
# Let's verify via API server to be safe.

from src.backend.api_server import app
from src.services.model_registry import ModelRegistry

class TestBacktestModelLoading(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.headers = {'X-API-Key': 'test_key'}
        
        # Setup Test Registry
        cls.test_dir = "tests/temp_backtest_loading"
        ModelRegistry.REGISTRY_PATH = f"{cls.test_dir}/registry.json"
        ModelRegistry.MODELS_DIR = f"{cls.test_dir}/archive"
        os.makedirs(ModelRegistry.MODELS_DIR, exist_ok=True)
        
        # Create a dummy model file
        cls.dummy_model_path = os.path.join(ModelRegistry.MODELS_DIR, "mlp_v9.9.pkl")
        with open(cls.dummy_model_path, 'wb') as f:
            f.write(b"dummy model content") # Real pickle would be better but we Mock the predictor loading anyway
            
        # Register it
        registry = ModelRegistry()
        registry.register_model("mlp", "v9.9", cls.dummy_model_path, {"params": {}}, metrics={})
        
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    @patch('src.models.lstm_predictor.MLPPredictor')
    @patch('src.data_pipeline.downloader.fetch_data')
    def test_backtest_loads_registry_model(self, mock_fetch, MockPredictor):
        """Test API loads model from registry"""
        import pandas as pd
        
        # Mock Data
        mock_fetch.return_value = pd.DataFrame({
            'Close': [100, 101, 102] * 20,
            'Volume': [1000] * 60,
            'High': [105] * 60,
            'Low': [95] * 60,
            'Open': [100] * 60
        }, index=pd.date_range('2024-01-01', periods=60))
        
        # Mock Predictor Instance
        mock_instance = MockPredictor.return_value
        mock_instance.load_model.return_value = True
        
        # Create a valid signal return matching the input df length
        input_len = 60
        res_df = mock_fetch.return_value.copy()
        res_df['Signal'] = [1] * input_len
        res_df['Position'] = [1] * input_len
        mock_instance.generate_signals.return_value = res_df
        
        # Call API
        res = self.client.get('/api/v1/backtest/run?ticker=BTC-USD&strategy=mlp', headers=self.headers)
        
        # Debug
        if res.status_code != 200:
            print(f"API Error: {res.get_json()}")
            
        self.assertEqual(res.status_code, 200)
        
        # Verify MLPPredictor was initialized with the correct path from registry
        # We expect the path to be the one we registered: mlp_v9.9.pkl (full path)
        # Note: ModelRegistry stores relative path usually, but api_server converts to absolute if needed.
        # But wait, ModelRegistry stores what we gave it.
        # Let's check call args.
        
        # Get the path passed to constructor
        call_args = MockPredictor.call_args
        if call_args:
             _, kwargs = call_args
             path_arg = kwargs.get('model_path')
             print(f"MLPPredictor initialized with: {path_arg}")
             self.assertTrue(path_arg.endswith("mlp_v9.9.pkl"))
        else:
            self.fail("MLPPredictor not initialized")

if __name__ == '__main__':
    unittest.main()
