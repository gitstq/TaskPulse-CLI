#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """任务类型枚举"""
    SHELL = "shell"
    PYTHON = "python"
    HTTP = "http"
    NOTIFICATION = "notification"
    DELAY = "delay"
    CONDITION = "condition"


@dataclass
class Task:
    """任务模型"""
    name: str
    command: str
    task_type: TaskType = TaskType.SHELL
    description: str = ""
    cron: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    working_dir: Optional[str] = None
    timeout: int = 300
    retries: int = 0
    retry_delay: int = 5
    enabled: bool = True
    notify_on: List[str] = field(default_factory=lambda: ["failed"])
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    condition: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["task_type"] = self.task_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建"""
        data = data.copy()
        if "task_type" in data:
            data["task_type"] = TaskType(data["task_type"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    task_name: str
    status: TaskStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: float = 0.0
    retry_count: int = 0
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class TaskGroup:
    """任务组模型"""
    name: str
    description: str = ""
    tasks: List[Task] = field(default_factory=list)
    parallel: bool = False
    enabled: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [t.to_dict() for t in self.tasks],
            "parallel": self.parallel,
            "enabled": self.enabled,
            "tags": self.tags,
        }


@dataclass
class ExecutionRecord:
    """执行记录"""
    execution_id: str
    group_name: str
    start_time: str
    end_time: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    results: List[TaskResult] = field(default_factory=list)
    trigger: str = "manual"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "execution_id": self.execution_id,
            "group_name": self.group_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status.value,
            "results": [r.to_dict() for r in self.results],
            "trigger": self.trigger,
        }
