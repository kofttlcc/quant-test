"""
config_service.py - 系統配置持久化服務
=======================================
版本: v1.0
功能: 讓 API 配置持久化到文件，後端重啟自動加載

存儲文件: config/app_config.json
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """應用配置"""
    # AI 配置
    gemini_api_url: str = "http://127.0.0.1:8045"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-pro-high"
    
    # 新聞 API
    tianapi_key: str = ""
    
    # 系統配置
    api_port: int = 5001
    enable_mock: bool = True
    
    # 更新時間
    updated_at: str = ""


class ConfigService:
    """
    配置持久化服務
    
    自動保存和加載配置到 JSON 文件
    """
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "app_config.json")
        self.config = AppConfig()
        
        # 確保目錄存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 啟動時加載配置
        self._load()
    
    def _load(self):
        """從文件加載配置"""
        if not os.path.exists(self.config_file):
            logger.info("配置文件不存在，使用默認配置")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新配置對象
            for key, value in data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            logger.info(f"配置已加載: {self.config_file}")
            logger.info(f"  - Gemini URL: {self.config.gemini_api_url}")
            logger.info(f"  - Gemini Key: {'*' * 8 if self.config.gemini_api_key else '未設置'}")
            
        except Exception as e:
            logger.error(f"加載配置失敗: {e}")
    
    def _save(self):
        """保存配置到文件"""
        try:
            self.config.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
            
            logger.info(f"配置已保存: {self.config_file}")
            
        except Exception as e:
            logger.error(f"保存配置失敗: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置項"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """設置配置項並保存"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self._save()
        else:
            logger.warning(f"未知配置項: {key}")
    
    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self._save()
    
    def get_all(self) -> Dict[str, Any]:
        """獲取所有配置"""
        return asdict(self.config)
    
    def update_ai_config(self, api_url: str = None, api_key: str = None, model: str = None):
        """更新 AI 配置"""
        if api_url:
            self.config.gemini_api_url = api_url
        if api_key:
            self.config.gemini_api_key = api_key
        if model:
            self.config.gemini_model = model
        self._save()
        
        # 同步更新 AI Proxy
        try:
            from src.services.ai_proxy import get_ai_proxy
            proxy = get_ai_proxy()
            proxy.update_config(api_url, api_key, model)
        except Exception as e:
            logger.warning(f"同步 AI Proxy 失敗: {e}")
    
    def get_ai_config(self) -> Dict[str, str]:
        """獲取 AI 配置"""
        return {
            "api_url": self.config.gemini_api_url,
            "api_key": self.config.gemini_api_key,
            "model": self.config.gemini_model
        }


# 單例
_service = ConfigService()


def get_config_service() -> ConfigService:
    """獲取配置服務單例"""
    return _service


def load_saved_config():
    """啟動時加載已保存的配置"""
    service = get_config_service()
    
    # 如果有保存的 AI 配置，自動應用
    if service.config.gemini_api_key:
        logger.info("發現已保存的 AI 配置，正在應用...")
        service.update_ai_config(
            service.config.gemini_api_url,
            service.config.gemini_api_key,
            service.config.gemini_model
        )


if __name__ == "__main__":
    print("--- SELF-TEST: config_service.py ---")
    
    # 使用臨時目錄測試
    service = ConfigService(config_dir="temp/config_test")
    
    print("\n[TEST] 默認配置:")
    print(f"  Gemini URL: {service.config.gemini_api_url}")
    print(f"  API Port: {service.config.api_port}")
    
    print("\n[TEST] 更新 AI 配置...")
    service.update_ai_config(
        api_url="http://127.0.0.1:8045",
        api_key="test-key-12345"
    )
    
    print("\n[TEST] 驗證保存...")
    # 重新加載
    service2 = ConfigService(config_dir="temp/config_test")
    print(f"  重新加載後 API Key: {service2.config.gemini_api_key}")
    
    print("\n--- SELF-TEST COMPLETE ---")
