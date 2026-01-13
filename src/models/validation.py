
import numpy as np
import pandas as pd
from itertools import combinations
import logging

logger = logging.getLogger(__name__)

class CombinatorialPurgedKFold:
    """
    Combinatorial Purged Cross-Validation (CPCV).
    Generates N choose K folds, ensuring purging and embargo to prevent leakage.
    
    Ref: Lopez de Prado, Advances in Financial Machine Learning.
    Skill: quant-ml-validation
    """

    def __init__(self, n_splits: int = 5, n_test_splits: int = 2, purge_window: int = 0, embargo_window: int = 0):
        """
        Args:
            n_splits (int): Total number of groups (N)
            n_test_splits (int): Number of groups in test set (k). Total paths = N choose k.
            purge_window (int): Number of bars to drop *before* test starts (if train precedes test).
            embargo_window (int): Number of bars to drop *after* test ends.
        """
        self.n_splits = n_splits
        self.n_test_splits = n_test_splits
        self.purge_window = purge_window
        self.embargo_window = embargo_window

    def split(self, X, y=None, groups=None):
        """
        Generate indices to split data into training and test set.
        
        Args:
            X: array-like of shape (n_samples, n_features)
            y: array-like of shape (n_samples,)
            groups: array-like of shape (n_samples,) - Not used, purely time-based.
            
        Yields:
            train_idx, test_idx
        """
        n_samples = len(X)
        indices = np.arange(n_samples)
        
        # 1. Split indices into N contiguous time groups
        # We can use array_split
        group_indices = np.array_split(indices, self.n_splits)
        
        # 2. Generate all combinations of k test groups
        # keys are group indices (0..N-1)
        all_groups = set(range(self.n_splits))
        
        for test_groups in combinations(all_groups, self.n_test_splits):
            test_groups = set(test_groups)
            train_groups = all_groups - test_groups
            
            # Construct raw test indices
            test_idx = np.concatenate([group_indices[i] for i in sorted(test_groups)])
            
            # Construct purified train indices
            train_idx_list = []
            
            # We need to handle purge/embargo for EACH test group block individually if they are separate?
            # Simplified: Iterate over each TR cluster. If it borders a TE cluster, apply purge/embargo.
            # Even simpler: For each sample in potential Train, is it "safe"?
            
            # Optimization: Mask-based
            # 1. Mark all as Train
            # 2. Mark Test
            # 3. Mark Purge/Embargo around Test
            
            mask = np.ones(n_samples, dtype=bool)
            
            # Mask out Test
            mask[test_idx] = False
            
            # Apply Purge/Embargo
            # For each contiguous block of test indices, computing boundaries
            # Since combinatorial, test groups might not be contiguous.
            # Let's iterate over each specific test group i in test_groups
            
            for g_id in test_groups:
                g_idxs = group_indices[g_id]
                t_start = g_idxs[0]
                t_end = g_idxs[-1]
                
                # Embargo: Drop Train samples immediately AFTER Test (t_end + 1 ... t_end + embargo)
                if self.embargo_window > 0:
                     mask[t_end + 1 : t_end + 1 + self.embargo_window] = False
                     
                # Purge: Drop Train samples immediately BEFORE Test (t_start - purge ... t_start - 1)
                # Why? Because Train[t-1] label might overlap into Test[t].
                # If label is "Return t to t+5", and Test starts at t,
                # then Train at t-4 (Label covers t-4 to t+1) overlaps Test.
                if self.purge_window > 0:
                    start_purge = max(0, t_start - self.purge_window)
                    mask[start_purge : t_start] = False
                    
            train_idx = indices[mask]
            
            yield train_idx, test_idx

if __name__ == "__main__":
    print("--- SELF-TEST: validation.py ---")
    data = np.arange(1000)
    
    cv = CombinatorialPurgedKFold(n_splits=5, n_test_splits=1, purge_window=10, embargo_window=10)
    
    for i, (train, test) in enumerate(cv.split(data)):
        print(f"Fold {i}: Train Size {len(train)}, Test Size {len(test)}")
        
        # Check Overlap
        overlap = set(train).intersection(set(test))
        if overlap:
            print(f"FAILURE: Train/Test Overlap: {overlap}")
        else:
            # Check gap
            # If Test is in middle, check boundaries
            test_start, test_end = test[0], test[-1]
            
            # Train before Test
            train_before = train[train < test_start]
            if len(train_before) > 0:
                gap_before = test_start - train_before[-1]
                if gap_before <= 10:
                    print(f"FAILURE: Purge Violation. Gap={gap_before}")
            
            # Train after Test
            train_after = train[train > test_end]
            if len(train_after) > 0:
                gap_after = train_after[0] - test_end
                if gap_after <= 10:
                     print(f"FAILURE: Embargo Violation. Gap={gap_after}")
                     
    print("If no FAILURE printed, Self-Test PASS.")

