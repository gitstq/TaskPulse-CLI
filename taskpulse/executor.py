#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务执行引擎
"""

import os
import sys
import time
import uuid
import subprocess
import threading
from datetime import datetime
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import Task, TaskResult, TaskStatus, TaskType
from .logger import get_logger

logger = get_logger(__name__)


class TaskExecutor:
    """任务执行器"""

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self._running_tasks: Dict[str, threading.Thread] = {}
        self._cancelled: set = set()

    def execute_task(
        self,
        task: Task,
        on_status_change: Optional[Callable] = None,
    ) -> TaskResult:
        """执行单个任务"""
        result = TaskResult(
            task_id=task.id,
            task_name=task.name,
            status=TaskStatus.PENDING,
            start_time=datetime.now().isoformat(),
        )

        if task.id in self._cancelled:
            result.status = TaskStatus.CANCELLED
            result.end_time = datetime.now().isoformat()
            return result

        logger.info(f"🚀 开始执行任务: {task.name}")
        result.status = TaskStatus.RUNNING
        if on_status_change:
            on_status_change(task.id, TaskStatus.RUNNING)

        start = time.time()
        retry = 0
        max_retries = task.retries

        while retry <= max_retries:
            try:
                if task.task_type == TaskType.SHELL:
                    self._execute_shell(task, result)
                elif task.task_type == TaskType.PYTHON:
                    self._execute_python(task, result)
                elif task.task_type == TaskType.HTTP:
                    self._execute_http(task, result)
                elif task.task_type == TaskType.NOTIFICATION:
                    self._execute_notification(task, result)
                elif task.task_type == TaskType.DELAY:
                    self._execute_delay(task, result)
                else:
                    result.status = TaskStatus.FAILED
                    result.error_message = f"不支持的任务类型: {task.task_type}"

                if result.status == TaskStatus.SUCCESS:
                    break

            except Exception as e:
                result.status = TaskStatus.FAILED
                result.error_message = str(e)
                result.stderr += f"\nException: {e}"
                logger.error(f"❌ 任务 {task.name} 执行异常: {e}")

            retry += 1
            if retry <= max_retries and result.status != TaskStatus.SUCCESS:
                result.retry_count = retry
                logger.warning(f"🔄 任务 {task.name} 第 {retry} 次重试...")
                time.sleep(task.retry_delay)

        result.duration = time.time() - start
        result.end_time = datetime.now().isoformat()

        if result.status == TaskStatus.SUCCESS:
            logger.info(f"✅ 任务 {task.name} 执行成功 ({result.duration:.2f}s)")
        else:
            logger.error(f"❌ 任务 {task.name} 执行失败: {result.error_message}")

        if on_status_change:
            on_status_change(task.id, result.status)

        return result

    def _execute_shell(self, task: Task, result: TaskResult):
        """执行 Shell 命令"""
        env = os.environ.copy()
        env.update(task.env)

        try:
            proc = subprocess.run(
                task.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=task.timeout,
                cwd=task.working_dir or os.getcwd(),
                env=env,
            )
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.exit_code = proc.returncode
            result.status = TaskStatus.SUCCESS if proc.returncode == 0 else TaskStatus.FAILED
            if proc.returncode != 0:
                result.error_message = f"命令退出码: {proc.returncode}"
        except subprocess.TimeoutExpired:
            result.status = TaskStatus.FAILED
            result.error_message = f"任务超时 ({task.timeout}s)"
            result.exit_code = -1

    def _execute_python(self, task: Task, result: TaskResult):
        """执行 Python 代码"""
        env = os.environ.copy()
        env.update(task.env)

        try:
            proc = subprocess.run(
                [sys.executable, "-c", task.command],
                capture_output=True,
                text=True,
                timeout=task.timeout,
                cwd=task.working_dir or os.getcwd(),
                env=env,
            )
            result.stdout = proc.stdout
            result.stderr = proc.stderr
            result.exit_code = proc.returncode
            result.status = TaskStatus.SUCCESS if proc.returncode == 0 else TaskStatus.FAILED
            if proc.returncode != 0:
                result.error_message = f"Python 代码执行失败，退出码: {proc.returncode}"
        except subprocess.TimeoutExpired:
            result.status = TaskStatus.FAILED
            result.error_message = f"任务超时 ({task.timeout}s)"
            result.exit_code = -1

    def _execute_http(self, task: Task, result: TaskResult):
        """执行 HTTP 请求"""
        import requests

        try:
            parts = task.command.split()
            method = "GET"
            url = parts[0]
            headers = {}
            data = None

            if len(parts) > 1:
                for i, part in enumerate(parts[1:]):
                    if part.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        method = part.upper()
                    elif part.startswith("http"):
                        url = part
                    elif part.startswith("-H"):
                        if i + 2 < len(parts):
                            header_parts = parts[i + 2].split(":", 1)
                            if len(header_parts) == 2:
                                headers[header_parts[0].strip()] = header_parts[1].strip()
                    elif part.startswith("-d"):
                        if i + 2 < len(parts):
                            data = parts[i + 2]

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=task.timeout,
            )
            result.stdout = f"Status: {response.status_code}\n{response.text[:2000]}"
            result.exit_code = 0 if response.status_code < 400 else response.status_code
            result.status = TaskStatus.SUCCESS if response.status_code < 400 else TaskStatus.FAILED
            if response.status_code >= 400:
                result.error_message = f"HTTP {response.status_code}"
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"HTTP 请求失败: {e}"
            result.exit_code = -1

    def _execute_notification(self, task: Task, result: TaskResult):
        """执行通知任务"""
        try:
            # 桌面通知
            if sys.platform == "darwin":
                subprocess.run(
                    ["osascript", "-e", f'display notification "{task.command}" with title "TaskPulse"'],
                    capture_output=True,
                )
            elif sys.platform == "linux":
                subprocess.run(
                    ["notify-send", "TaskPulse", task.command],
                    capture_output=True,
                )
            result.stdout = f"通知已发送: {task.command}"
            result.status = TaskStatus.SUCCESS
        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error_message = f"通知发送失败: {e}"

    def _execute_delay(self, task: Task, result: TaskResult):
        """执行延迟任务"""
        try:
            delay_seconds = int(task.command)
            time.sleep(delay_seconds)
            result.stdout = f"延迟 {delay_seconds} 秒完成"
            result.status = TaskStatus.SUCCESS
        except ValueError:
            result.status = TaskStatus.FAILED
            result.error_message = "延迟任务需要指定秒数"

    def execute_group(
        self,
        tasks: List[Task],
        parallel: bool = False,
        on_status_change: Optional[Callable] = None,
    ) -> List[TaskResult]:
        """执行任务组"""
        results = []
        task_map = {t.id: t for t in tasks}
        completed = set()

        if parallel:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.execute_task, task, on_status_change): task
                    for task in tasks
                }
                for future in as_completed(futures):
                    task = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        completed.add(task.id)
                    except Exception as e:
                        results.append(TaskResult(
                            task_id=task.id,
                            task_name=task.name,
                            status=TaskStatus.FAILED,
                            error_message=str(e),
                        ))
        else:
            # 串行执行，处理依赖关系
            pending = set(t.id for t in tasks)
            while pending:
                executable = [
                    tid for tid in pending
                    if all(dep in completed for dep in task_map[tid].depends_on)
                ]
                if not executable:
                    # 依赖循环检测
                    for tid in pending:
                        results.append(TaskResult(
                            task_id=tid,
                            task_name=task_map[tid].name,
                            status=TaskStatus.FAILED,
                            error_message="依赖循环或缺失",
                        ))
                    break

                for tid in executable:
                    task = task_map[tid]
                    result = self.execute_task(task, on_status_change)
                    results.append(result)
                    completed.add(tid)
                    pending.remove(tid)

        return results

    def cancel_task(self, task_id: str):
        """取消任务"""
        self._cancelled.add(task_id)
        logger.info(f"🛑 任务 {task_id} 已标记取消")

    def cancel_all(self):
        """取消所有任务"""
        self._cancelled.update(self._running_tasks.keys())
        logger.info("🛑 所有任务已标记取消")
