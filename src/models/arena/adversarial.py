
"""
adversarial.py - Adversarial Noise Generator (Phase 7.3)
========================================================
Injects controlled noise into financial time series to
train robust ML models.
"""

import numpy as np
import pandas as pd

class NoiseGenerator:
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
        
    def add_gaussian_noise(self, data: np.ndarray, std_dev=0.01) -> np.ndarray:
        """
        Add Gaussian noise to data.
        """
        noise = self.rng.normal(0, std_dev, size=data.shape)
        return data + noise
        
    def add_price_spike(self, data: np.ndarray, prob=0.01, magnitude=0.05) -> np.ndarray:
        """
        Randomly spike prices to simulate flash crashes/pumps.
        """
        data_mod = data.copy()
        mask = self.rng.random(size=data.shape) < prob
        
        # 50% chance of positive or negative spike
        signs = self.rng.choice([-1, 1], size=data.shape)
        
        spikes = data_mod * magnitude * signs * mask
        return data_mod + spikes

class AdversarialTrainer:
    def __init__(self, base_model):
        self.model = base_model
        self.noise_gen = NoiseGenerator()
        
    def train_robust(self, X, y, noise_level=0.01):
        """
        Train on augmented data (Original + Noisy).
        """
        print(f"AdvTrain: Generating adversarial examples (Noise={noise_level})...")
        
        X_noisy = self.noise_gen.add_gaussian_noise(X, std_dev=noise_level)
        
        # Combine
        X_combined = np.vstack([X, X_noisy])
        y_combined = np.hstack([y, y]) # Assuming labels don't change for small noise
        
        # In reality, big noise might change label (Turn Bull to Bear), 
        # but for robustness we assume noise shouldn't flip the underlying trend detection immediately
        # or we want model to be insensitive to it.
        
        print(f"AdvTrain: Fitting on {len(X_combined)} samples...")
        self.model.fit(X_combined, y_combined)
        print("AdvTrain: Robust training complete.")
