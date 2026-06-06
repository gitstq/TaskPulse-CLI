#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据持久化模块
"""

import os
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import Task, TaskGroup, TaskResult, ExecutionRecord, TaskStatus
from .logger import get_logger

logger = get_logger(__name__)


class TaskStorage:
    """任务存储管理器"""

    def __init__(self, tasks_file: str = "tasks.yaml", history_dir: str = "history"):
        self.tasks_file = tasks_file
        self.history_dir = history_dir
        os.makedirs(history_dir, exist_ok=True)

    def load_tasks(self) -> List[Task]:
        """加载任务列表"""
        if not os.path.exists(self.tasks_file):
            return []

        try:
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                if self.tasks_file.endswith(".json"):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f) or {}

            tasks = []
            if isinstance(data, dict):
                # 支持 groups 和 tasks 两种格式
                if "groups" in data:
                    for group_data in data["groups"]:
                        for task_data in group_data.get("tasks", []):
                            tasks.append(Task.from_dict(task_data))
                elif "tasks" in data:
                    for task_data in data["tasks"]:
                        tasks.append(Task.from_dict(task_data))
            elif isinstance(data, list):
                for task_data in data:
                    tasks.append(Task.from_dict(task_data))

            logger.info(f"📂 已加载 {len(tasks)} 个任务")
            return tasks
        except Exception as e:
            logger.error(f"❌ 加载任务失败: {e}")
            return []

    def save_tasks(self, tasks: List[Task], groups: Optional[List[TaskGroup]] = None):
        """保存任务列表"""
        try:
            data = {"version": "1.0", "updated_at": datetime.now().isoformat()}

            if groups:
                data["groups"] = [g.to_dict() for g in groups]
            else:
                data["tasks"] = [t.to_dict() for t in tasks]

            with open(self.tasks_file, "w", encoding="utf-8") as f:
                if self.tasks_file.endswith(".json"):
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"💾 已保存 {len(tasks)} 个任务到 {self.tasks_file}")
        except Exception as e:
            logger.error(f"❌ 保存任务失败: {e}")

    def load_groups(self) -> List[TaskGroup]:
        """加载任务组"""
        if not os.path.exists(self.tasks_file):
            return []

        try:
            with open(self.tasks_file, "r", encoding="utf-8") as f:
                if self.tasks_file.endswith(".json"):
                    data = json.load(f)
                else:
                    data = yaml.safe_load(f) or {}

            groups = []
            if isinstance(data, dict) and "groups" in data:
                for group_data in data["groups"]:
                    group = TaskGroup(
                        name=group_data.get("name", "Unnamed"),
                        description=group_data.get("description", ""),
                        parallel=group_data.get("parallel", False),
                        enabled=group_data.get("enabled", True),
                        id=group_data.get("id", ""),
                        tags=group_data.get("tags", []),
                    )
                    for task_data in group_data.get("tasks", []):
                        group.tasks.append(Task.from_dict(task_data))
                    groups.append(group)

            return groups
        except Exception as e:
            logger.error(f"❌ 加载任务组失败: {e}")
            return []

    def save_execution(self, record: ExecutionRecord):
        """保存执行记录"""
        try:
            filename = f"execution_{record.execution_id}_{datetime.now().strftime('%Y%m%d')}.json"
            filepath = os.path.join(self.history_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"💾 执行记录已保存: {filename}")
        except Exception as e:
            logger.error(f"❌ 保存执行记录失败: {e}")

    def load_executions(self, limit: int = 50) -> List[ExecutionRecord]:
        """加载执行记录"""
        records = []
        history_path = Path(self.history_dir)

        if not history_path.exists():
            return records

        files = sorted(
            history_path.glob("execution_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]

        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                record = ExecutionRecord(
                    execution_id=data.get("execution_id", ""),
                    group_name=data.get("group_name", ""),
                    start_time=data.get("start_time", ""),
                    end_time=data.get("end_time"),
                    status=TaskStatus(data.get("status", "pending")),
                    trigger=data.get("trigger", "manual"),
                )
                for result_data in data.get("results", []):
                    record.results.append(TaskResult(
                        task_id=result_data.get("task_id", ""),
                        task_name=result_data.get("task_name", ""),
                        status=TaskStatus(result_data.get("status", "pending")),
                        stdout=result_data.get("stdout", ""),
                        stderr=result_data.get("stderr", ""),
                        exit_code=result_data.get("exit_code", 0),
                        start_time=result_data.get("start_time"),
                        end_time=result_data.get("end_time"),
                        duration=result_data.get("duration", 0.0),
                        retry_count=result_data.get("retry_count", 0),
                        error_message=result_data.get("error_message", ""),
                    ))
                records.append(record)
            except Exception as e:
                logger.error(f"❌ 加载执行记录失败 {file}: {e}")

        return records

    def get_task_stats(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        executions = self.load_executions(limit=1000)

        total = len(executions)
        success = sum(1 for e in executions if e.status == TaskStatus.SUCCESS)
        failed = sum(1 for e in executions if e.status == TaskStatus.FAILED)

        return {
            "total_executions": total,
            "success_count": success,
            "failed_count": failed,
            "success_rate": f"{(success / total * 100):.1f}%" if total > 0 else "N/A",
            "recent_executions": [
                {
                    "id": e.execution_id,
                    "group": e.group_name,
                    "status": e.status.value,
                    "start": e.start_time,
                }
                for e in executions[:10]
            ],
        }
