# Logging Configuration Module
# MINOR-004 FIX: 統一日誌配置，避免多個模塊重複調用 basicConfig

import logging
import os
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """
    統一日誌配置
    
    這個函數應該在應用啟動時調用一次，而非在每個模塊中調用。
    
    Args:
        level: 日誌級別 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 可選的日誌文件路徑
        format_string: 日誌格式字符串
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 配置根日誌記錄器
    handlers = []
    
    # 控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(format_string))
    handlers.append(console_handler)
    
    # 文件處理器（如果指定）
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(format_string))
        handlers.append(file_handler)
    
    # 配置根記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # 清除現有處理器
    root_logger.handlers.clear()
    
    for handler in handlers:
        root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    獲取模塊日誌記錄器
    
    使用此函數替代 logging.getLogger() 以確保一致性
    
    Args:
        name: 通常使用 __name__
        
    Returns:
        配置好的日誌記錄器
    """
    return logging.getLogger(name)


# 默認配置
_initialized = False

def ensure_logging_setup():
    """確保日誌已初始化（懶加載）"""
    global _initialized
    if not _initialized:
        log_level = os.environ.get('LOG_LEVEL', 'INFO')
        log_file = os.environ.get('LOG_FILE')
        setup_logging(level=log_level, log_file=log_file)
        _initialized = True
