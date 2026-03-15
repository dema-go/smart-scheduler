"""
日志配置模块
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import settings


# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> logging.Logger:
    """配置应用日志"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 根日志器
    logger = logging.getLogger("scheduler")
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件输出 - 普通日志
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)

    # 文件输出 - 错误日志
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(console_formatter)
    logger.addHandler(error_handler)

    return logger


# 全局日志实例
logger = setup_logging()
