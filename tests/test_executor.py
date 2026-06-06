#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行器单元测试
"""

import pytest
from taskpulse.executor import TaskExecutor
from taskpulse.models import Task, TaskStatus, TaskType


class TestTaskExecutor:
    def setup_method(self):
        self.executor = TaskExecutor()

    def test_execute_shell_task(self):
        task = Task(
            name="shell_test",
            command="echo 'hello world'",
            task_type=TaskType.SHELL,
        )
        result = self.executor.execute_task(task)
        assert result.status == TaskStatus.SUCCESS
        assert "hello world" in result.stdout
        assert result.exit_code == 0

    def test_execute_python_task(self):
        task = Task(
            name="python_test",
            command="print('hello from python')",
            task_type=TaskType.PYTHON,
        )
        result = self.executor.execute_task(task)
        assert result.status == TaskStatus.SUCCESS
        assert "hello from python" in result.stdout

    def test_execute_failed_task(self):
        task = Task(
            name="fail_test",
            command="exit 1",
            task_type=TaskType.SHELL,
        )
        result = self.executor.execute_task(task)
        assert result.status == TaskStatus.FAILED
        assert result.exit_code == 1

    def test_execute_delay_task(self):
        task = Task(
            name="delay_test",
            command="1",
            task_type=TaskType.DELAY,
        )
        result = self.executor.execute_task(task)
        assert result.status == TaskStatus.SUCCESS
        assert "延迟 1 秒完成" in result.stdout

    def test_task_timeout(self):
        task = Task(
            name="timeout_test",
            command="sleep 10",
            task_type=TaskType.SHELL,
            timeout=1,
        )
        result = self.executor.execute_task(task)
        assert result.status == TaskStatus.FAILED
        assert "超时" in result.error_message

    def test_task_retry(self):
        task = Task(
            name="retry_test",
            command="exit 1",
            task_type=TaskType.SHELL,
            retries=2,
            retry_delay=0,
        )
        result = self.executor.execute_task(task)
        assert result.status == TaskStatus.FAILED
        assert result.retry_count == 2
