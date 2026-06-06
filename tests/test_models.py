#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型单元测试
"""

import pytest
from taskpulse.models import Task, TaskResult, TaskGroup, TaskStatus, TaskType


class TestTask:
    def test_task_creation(self):
        task = Task(
            name="test_task",
            command="echo hello",
            task_type=TaskType.SHELL,
        )
        assert task.name == "test_task"
        assert task.command == "echo hello"
        assert task.task_type == TaskType.SHELL
        assert task.enabled is True
        assert len(task.id) == 8

    def test_task_to_dict(self):
        task = Task(
            name="test_task",
            command="echo hello",
            task_type=TaskType.SHELL,
            description="A test task",
        )
        data = task.to_dict()
        assert data["name"] == "test_task"
        assert data["task_type"] == "shell"
        assert data["description"] == "A test task"

    def test_task_from_dict(self):
        data = {
            "name": "test_task",
            "command": "echo hello",
            "task_type": "shell",
            "description": "A test task",
        }
        task = Task.from_dict(data)
        assert task.name == "test_task"
        assert task.task_type == TaskType.SHELL


class TestTaskResult:
    def test_result_creation(self):
        result = TaskResult(
            task_id="abc123",
            task_name="test",
            status=TaskStatus.SUCCESS,
        )
        assert result.task_id == "abc123"
        assert result.status == TaskStatus.SUCCESS
        assert result.exit_code == 0


class TestTaskGroup:
    def test_group_creation(self):
        task = Task(name="t1", command="echo 1", task_type=TaskType.SHELL)
        group = TaskGroup(
            name="test_group",
            description="A test group",
            tasks=[task],
        )
        assert group.name == "test_group"
        assert len(group.tasks) == 1
        assert group.parallel is False
