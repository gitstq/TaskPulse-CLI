#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理模块
"""

import os
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_logger(name: str, log_dir: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """获取配置好的日志记录器"""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(
            log_dir,
            f"taskpulse_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


class LogManager:
    """日志管理器"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def get_log_files(self) -> list:
        """获取所有日志文件"""
        log_path = Path(self.log_dir)
        if not log_path.exists():
            return []
        return sorted(
            [f.name for f in log_path.glob("taskpulse_*.log")],
            reverse=True
        )

    def read_log(self, filename: str, lines: int = 100) -> str:
        """读取日志文件"""
        filepath = os.path.join(self.log_dir, filename)
        if not os.path.exists(filepath):
            return ""

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                return "".join(all_lines[-lines:])
        except Exception as e:
            return f"读取日志失败: {e}"

    def clean_old_logs(self, days: int = 7):
        """清理旧日志"""
        import time

        cutoff = time.time() - (days * 86400)
        log_path = Path(self.log_dir)

        for log_file in log_path.glob("taskpulse_*.log"):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                print(f"🗑️  已删除旧日志: {log_file.name}")
