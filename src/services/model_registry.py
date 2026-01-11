import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

# Ensure project root is reachable
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

logger = logging.getLogger(__name__)

class ModelRegistry:
    """
    Model Versioning and Registry Service (V2).
    負責管理 AI 模型版本，記錄調參歷史。
    """
    
    REGISTRY_PATH = "data/model_registry/registry.json"
    MODELS_DIR = "data/model_registry/archive"
    
    def __init__(self):
        # Ensure directories exist relative to workspace root
        # Assuming execution from root or src/backend, but best to be absolute or robust relative
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
        self.full_registry_path = os.path.join(self.root_dir, self.REGISTRY_PATH)
        self.full_models_dir = os.path.join(self.root_dir, self.MODELS_DIR)
        
        os.makedirs(self.full_models_dir, exist_ok=True)
        self._load_registry()
        
    def _load_registry(self):
        """Load registry from disk."""
        if os.path.exists(self.full_registry_path):
            try:
                with open(self.full_registry_path, 'r') as f:
                    self.registry = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")
                self.registry = {"models": {}}
        else:
            self.registry = {"models": {}}
            
    def _save_registry(self):
        """Save registry to disk."""
        try:
            with open(self.full_registry_path, 'w') as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
            
    def get_next_version(self, model_type: str) -> str:
        """
        Get next version string for a model type (e.g., 'v1.1').
        Format: v{Major}.{Minor}
        """
        history = self.registry["models"].get(model_type, [])
        if not history:
            return "v1.0"
            
        last_version = history[-1]["version"]
        # Parse version
        try:
            major, minor = map(int, last_version.replace("v", "").split("."))
            if minor >= 9:
                major += 1
                minor = 0
            else:
                minor += 1
            return f"v{major}.{minor}"
        except Exception:
            return f"v{len(history) + 1}.0"
            
    def register_model(self, model_type: str, version: str, path: str, params: Dict[str, Any], metrics: Optional[Dict] = None):
        """
        Register a new model version.
        """
        if model_type not in self.registry["models"]:
            self.registry["models"][model_type] = []
            
        # Store relative path for portability
        if os.path.isabs(path):
            rel_path = os.path.relpath(path, self.root_dir)
        else:
            rel_path = path

        entry = {
            "version": version,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "path": rel_path,
            "params": params,
            "metrics": metrics or {}
        }
        
        self.registry["models"][model_type].append(entry)
        self._save_registry()
        logger.info(f"Registered model {model_type} version {version}")
        
    def get_archive_path(self, model_type: str, version: str) -> str:
        """Generate archive path for a model version (Absolute)."""
        filename = f"{model_type}_{version}.pkl"
        return os.path.join(self.full_models_dir, filename)

    def list_models(self, model_type: str = None) -> List[Dict]:
        """List all models or filter by type."""
        if model_type:
            return self.registry["models"].get(model_type, [])
        else:
            all_models = []
            for m_type, versions in self.registry["models"].items():
                for v in versions:
                    v['type'] = m_type
                    all_models.append(v)
            return all_models

    def delete_model(self, model_type: str, version: str) -> bool:
        """Delete a specific model version."""
        if model_type not in self.registry["models"]:
            return False
            
        models = self.registry["models"][model_type]
        for i, m in enumerate(models):
            if m['version'] == version:
                # Remove file
                full_path = os.path.join(self.root_dir, m['path'])
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except OSError as e:
                        logger.warning(f"Failed to remove model file {full_path}: {e}")
                
                # Remove registry entry
                self.registry["models"][model_type].pop(i)
                self._save_registry()
                return True
        return False

# Global Instance
_registry = None

def get_model_registry():
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry
