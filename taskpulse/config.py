#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "general": {
        "timezone": "Asia/Shanghai",
        "log_level": "INFO",
        "max_history": 100,
        "auto_save": True,
    },
    "scheduler": {
        "check_interval": 1,
        "max_concurrent": 5,
        "retry_count": 3,
        "retry_delay": 5,
    },
    "notifications": {
        "enabled": False,
        "webhook_url": "",
        "email": {
            "enabled": False,
            "smtp_host": "",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "to_address": "",
        },
        "desktop": {
            "enabled": True,
        },
    },
    "ai": {
        "enabled": False,
        "provider": "openai",
        "api_key": "",
        "api_base": "",
        "model": "gpt-3.5-turbo",
        "max_tokens": 2048,
        "temperature": 0.7,
    },
    "tasks_file": "tasks.yaml",
    "logs_dir": "logs",
    "history_dir": "history",
}


class Config:
    """配置管理类"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.data = self._load_config()

    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        home = Path.home()
        config_dir = home / ".config" / "taskpulse"
        config_dir.mkdir(parents=True, exist_ok=True)
        return str(config_dir / "config.yaml")

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    if self.config_path.endswith(".json"):
                        user_config = json.load(f)
                    else:
                        user_config = yaml.safe_load(f) or {}
                config = self._deep_merge(DEFAULT_CONFIG.copy(), user_config)
                return config
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置: {e}")
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def save(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.data, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持点号分隔的路径"""
        keys = key.split(".")
        value = self.data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """设置配置项，支持点号分隔的路径"""
        keys = key.split(".")
        target = self.data
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        if self.get("general.auto_save", True):
            self.save()

    @property
    def tasks_file(self) -> str:
        """获取任务文件路径"""
        return self.get("tasks_file", "tasks.yaml")

    @property
    def logs_dir(self) -> str:
        """获取日志目录"""
        return self.get("logs_dir", "logs")

    @property
    def history_dir(self) -> str:
        """获取历史记录目录"""
        return self.get("history_dir", "history")
