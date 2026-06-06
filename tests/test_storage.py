#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储模块单元测试
"""

import os
import tempfile
import pytest
from taskpulse.storage import TaskStorage
from taskpulse.models import Task, TaskGroup, TaskType, TaskStatus, ExecutionRecord, TaskResult


class TestTaskStorage:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.tasks_file = os.path.join(self.temp_dir, "test_tasks.yaml")
        self.history_dir = os.path.join(self.temp_dir, "history")
        self.storage = TaskStorage(self.tasks_file, self.history_dir)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_tasks(self):
        tasks = [
            Task(name="t1", command="echo 1", task_type=TaskType.SHELL),
            Task(name="t2", command="echo 2", task_type=TaskType.SHELL),
        ]
        self.storage.save_tasks(tasks)
        loaded = self.storage.load_tasks()
        assert len(loaded) == 2
        assert loaded[0].name == "t1"
        assert loaded[1].name == "t2"

    def test_save_and_load_groups(self):
        group = TaskGroup(
            name="test_group",
            description="A test group",
            tasks=[
                Task(name="t1", command="echo 1", task_type=TaskType.SHELL),
            ],
        )
        self.storage.save_tasks([], groups=[group])
        loaded_groups = self.storage.load_groups()
        assert len(loaded_groups) == 1
        assert loaded_groups[0].name == "test_group"
        assert len(loaded_groups[0].tasks) == 1

    def test_save_and_load_execution(self):
        record = ExecutionRecord(
            execution_id="test123",
            group_name="default",
            start_time="2024-01-01T00:00:00",
            status=TaskStatus.SUCCESS,
            trigger="manual",
        )
        record.results.append(TaskResult(
            task_id="t1",
            task_name="task1",
            status=TaskStatus.SUCCESS,
            stdout="hello",
        ))
        self.storage.save_execution(record)
        loaded = self.storage.load_executions(limit=10)
        assert len(loaded) == 1
        assert loaded[0].execution_id == "test123"
        assert len(loaded[0].results) == 1

    def test_get_task_stats(self):
        # 创建一些执行记录
        for i in range(5):
            record = ExecutionRecord(
                execution_id=f"exec{i}",
                group_name="default",
                start_time="2024-01-01T00:00:00",
                status=TaskStatus.SUCCESS if i < 3 else TaskStatus.FAILED,
                trigger="manual",
            )
            self.storage.save_execution(record)

        stats = self.storage.get_task_stats()
        assert stats["total_executions"] == 5
        assert stats["success_count"] == 3
        assert stats["failed_count"] == 2
