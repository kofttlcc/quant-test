# Model Configuration
# MINOR-001 FIX: 統一模型路徑配置，從環境變量或配置文件讀取

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelPaths:
    """模型路徑配置"""
    
    # 機器學習模型
    mlp_model: str = ""
    lgbm_model: str = ""
    tree_model: str = ""
    
    # 緩存目錄
    cache_dir: str = ""
    
    def __post_init__(self):
        """從環境變量加載，如果未設置則使用默認值"""
        base_dir = os.environ.get('QUANT_MODEL_DIR', 'temp/ml_models')
        cache_base = os.environ.get('QUANT_CACHE_DIR', 'quant_data')
        
        self.mlp_model = self.mlp_model or os.path.join(base_dir, 'mlp_model.pkl')
        self.lgbm_model = self.lgbm_model or os.path.join(base_dir, 'lgbm_model.pkl')
        self.tree_model = self.tree_model or os.path.join(base_dir, 'tree_model.pkl')
        self.cache_dir = self.cache_dir or cache_base
        
        # 確保目錄存在
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(cache_base, exist_ok=True)


# 全局單例
_model_paths: Optional[ModelPaths] = None


def get_model_paths() -> ModelPaths:
    """獲取模型路徑配置（單例）"""
    global _model_paths
    if _model_paths is None:
        _model_paths = ModelPaths()
    return _model_paths


def get_model_path(model_type: str) -> str:
    """
    獲取指定模型的路徑
    
    Args:
        model_type: 模型類型 ('mlp', 'lgbm', 'tree')
        
    Returns:
        模型文件路徑
    """
    paths = get_model_paths()
    mapping = {
        'mlp': paths.mlp_model,
        'lgbm': paths.lgbm_model,
        'tree': paths.tree_model
    }
    return mapping.get(model_type, paths.mlp_model)
