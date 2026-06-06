#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时调度模块
"""

import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Callable

import schedule

from .models import Task, TaskResult, TaskStatus
from .executor import TaskExecutor
from .logger import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """任务调度器"""

    def __init__(self, executor: Optional[TaskExecutor] = None, check_interval: int = 1):
        self.executor = executor or TaskExecutor()
        self.check_interval = check_interval
        self._scheduled_tasks: Dict[str, Task] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()

    def add_task(self, task: Task):
        """添加定时任务"""
        if not task.cron:
            logger.warning(f"任务 {task.name} 没有 cron 表达式，跳过调度")
            return

        with self._lock:
            self._scheduled_tasks[task.id] = task

        # 解析 cron 表达式并注册到 schedule
        self._register_cron(task)
        logger.info(f"📅 任务 {task.name} 已添加到调度器")

    def _register_cron(self, task: Task):
        """注册 cron 任务"""
        cron_parts = task.cron.split()
        if len(cron_parts) != 5:
            logger.error(f"任务 {task.name} 的 cron 表达式格式错误: {task.cron}")
            return

        minute, hour, day, month, day_of_week = cron_parts

        job = schedule.every()

        # 简化版 cron 解析
        if minute != "*":
            if "/" in minute:
                interval = int(minute.split("/")[1])
                job = job.minutes.do(lambda: None)
                # 重新创建正确的间隔任务
                job = schedule.every(interval).minutes
            else:
                job = schedule.every().day.at(f"{int(hour):02d}:{int(minute):02d}")
        elif hour != "*":
            job = schedule.every().day.at(f"{int(hour):02d}:00")
        else:
            job = schedule.every(1).minutes

        job.do(self._run_scheduled_task, task)

    def _run_scheduled_task(self, task: Task):
        """运行定时任务"""
        if not task.enabled:
            return

        logger.info(f"⏰ 定时触发任务: {task.name}")
        result = self.executor.execute_task(task)

        for callback in self._callbacks:
            try:
                callback(task, result)
            except Exception as e:
                logger.error(f"回调执行失败: {e}")

    def remove_task(self, task_id: str):
        """移除定时任务"""
        with self._lock:
            if task_id in self._scheduled_tasks:
                del self._scheduled_tasks[task_id]
                schedule.clear(task_id)
                logger.info(f"🗑️  任务 {task_id} 已从调度器移除")

    def start(self):
        """启动调度器"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("🚀 调度器已启动")

    def _run_loop(self):
        """调度主循环"""
        while self._running:
            schedule.run_pending()
            time.sleep(self.check_interval)

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        schedule.clear()
        logger.info("🛑 调度器已停止")

    def add_callback(self, callback: Callable):
        """添加执行回调"""
        self._callbacks.append(callback)

    def get_scheduled_tasks(self) -> List[Task]:
        """获取所有已调度任务"""
        with self._lock:
            return list(self._scheduled_tasks.values())

    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self._running
