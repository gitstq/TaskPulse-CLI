#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终端 TUI 界面
"""

import time
import threading
from datetime import datetime
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from .models import Task, TaskResult, TaskStatus, TaskGroup
from .executor import TaskExecutor
from .scheduler import TaskScheduler
from .storage import TaskStorage
from .logger import get_logger

logger = get_logger(__name__)
console = Console()


class TaskPulseTUI:
    """TaskPulse 终端界面"""

    def __init__(self, storage: TaskStorage, executor: TaskExecutor, scheduler: TaskScheduler):
        self.storage = storage
        self.executor = executor
        self.scheduler = scheduler
        self.tasks: List[Task] = []
        self.groups: List[TaskGroup] = []
        self.results: List[TaskResult] = []
        self.selected_index = 0
        self.running = False
        self._refresh_thread: Optional[threading.Thread] = None

    def load_data(self):
        """加载数据"""
        self.tasks = self.storage.load_tasks()
        self.groups = self.storage.load_groups()

    def run(self):
        """运行 TUI"""
        self.load_data()
        self.running = True

        console.print("\n[bold cyan]🚀 TaskPulse-CLI 终端监控界面[/bold cyan]\n")
        console.print("[dim]按 Ctrl+C 退出[/dim]\n")

        try:
            with Live(self._render(), refresh_per_second=2) as live:
                while self.running:
                    self._update_data()
                    live.update(self._render())
                    time.sleep(0.5)
        except KeyboardInterrupt:
            self.running = False
            console.print("\n[yellow]👋 已退出监控界面[/yellow]")

    def _update_data(self):
        """更新数据"""
        # 定期刷新任务列表
        if not hasattr(self, '_last_refresh') or time.time() - self._last_refresh > 5:
            self.tasks = self.storage.load_tasks()
            self.groups = self.storage.load_groups()
            self._last_refresh = time.time()

    def _render(self) -> Layout:
        """渲染界面"""
        layout = Layout()

        # 标题
        header = Panel(
            Text("TaskPulse-CLI 🚀 终端智能任务调度器", style="bold cyan", justify="center"),
            border_style="cyan",
        )

        # 任务列表
        task_table = self._render_task_table()

        # 状态面板
        status_panel = self._render_status_panel()

        # 最近执行记录
        history_panel = self._render_history_panel()

        layout.split_column(
            Layout(header, size=3),
            Layout(task_table, ratio=2),
            Layout(status_panel, size=8),
            Layout(history_panel, ratio=1),
        )

        return layout

    def _render_task_table(self) -> Panel:
        """渲染任务表格"""
        table = Table(
            title="📋 任务列表",
            border_style="blue",
            header_style="bold white on blue",
        )
        table.add_column("ID", style="dim", width=8)
        table.add_column("名称", style="cyan", min_width=20)
        table.add_column("类型", style="green", width=12)
        table.add_column("状态", style="yellow", width=10)
        table.add_column("定时", style="magenta", width=15)
        table.add_column("描述", style="white", min_width=30)

        for i, task in enumerate(self.tasks[:20]):
            status_icon = "🟢" if task.enabled else "🔴"
            cron_str = task.cron or "-"
            table.add_row(
                task.id,
                task.name,
                task.task_type.value,
                f"{status_icon} {'启用' if task.enabled else '禁用'}",
                cron_str,
                task.description[:40] + "..." if len(task.description) > 40 else task.description,
            )

        return Panel(table, border_style="blue")

    def _render_status_panel(self) -> Panel:
        """渲染状态面板"""
        scheduler_status = "🟢 运行中" if self.scheduler.is_running() else "🔴 已停止"

        stats = self.storage.get_task_stats()

        content = Text()
        content.append(f"调度器状态: {scheduler_status}\n", style="bold")
        content.append(f"任务总数: {len(self.tasks)}\n")
        content.append(f"任务组数: {len(self.groups)}\n")
        content.append(f"总执行次数: {stats.get('total_executions', 0)}\n")
        content.append(f"成功次数: {stats.get('success_count', 0)}\n")
        content.append(f"失败次数: {stats.get('failed_count', 0)}\n")
        content.append(f"成功率: {stats.get('success_rate', 'N/A')}\n")

        return Panel(content, title="📊 系统状态", border_style="green")

    def _render_history_panel(self) -> Panel:
        """渲染历史记录面板"""
        table = Table(
            title="📜 最近执行记录",
            border_style="yellow",
            header_style="bold white on yellow",
        )
        table.add_column("执行ID", style="dim", width=12)
        table.add_column("任务组", style="cyan", min_width=15)
        table.add_column("状态", style="green", width=10)
        table.add_column("触发方式", style="magenta", width=10)
        table.add_column("开始时间", style="white", width=20)

        executions = self.storage.load_executions(limit=10)
        for exec_record in executions:
            status_color = "green" if exec_record.status == TaskStatus.SUCCESS else "red"
            table.add_row(
                exec_record.execution_id[:8],
                exec_record.group_name,
                f"[{status_color}]{exec_record.status.value}[/{status_color}]",
                exec_record.trigger,
                exec_record.start_time[:19] if exec_record.start_time else "-",
            )

        return Panel(table, border_style="yellow")

    def run_task_interactive(self, task_id: Optional[str] = None):
        """交互式运行任务"""
        self.load_data()

        if not self.tasks:
            console.print("[yellow]⚠️  暂无任务，请先添加任务[/yellow]")
            return

        if task_id:
            task = next((t for t in self.tasks if t.id == task_id), None)
            if not task:
                console.print(f"[red]❌ 未找到任务: {task_id}[/red]")
                return
        else:
            # 显示任务列表供选择
            console.print("\n[bold]📋 可用任务:[/bold]\n")
            for i, task in enumerate(self.tasks):
                console.print(f"  [{i+1}] {task.name} ({task.task_type.value})")

            try:
                choice = int(console.input("\n请选择任务编号: ")) - 1
                if 0 <= choice < len(self.tasks):
                    task = self.tasks[choice]
                else:
                    console.print("[red]❌ 无效选择[/red]")
                    return
            except ValueError:
                console.print("[red]❌ 请输入数字[/red]")
                return

        console.print(f"\n[bold cyan]🚀 执行任务: {task.name}[/bold cyan]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_progress = progress.add_task(f"执行 {task.name}...", total=None)
            result = self.executor.execute_task(task)
            progress.update(task_progress, completed=True)

        # 显示结果
        if result.status == TaskStatus.SUCCESS:
            console.print(f"\n[green]✅ 任务执行成功 ({result.duration:.2f}s)[/green]")
        else:
            console.print(f"\n[red]❌ 任务执行失败[/red]")

        if result.stdout:
            console.print(Panel(result.stdout, title="📤 输出", border_style="green"))
        if result.stderr:
            console.print(Panel(result.stderr, title="📛 错误", border_style="red"))

        # 保存执行记录
        from .models import ExecutionRecord
        record = ExecutionRecord(
            execution_id=result.task_id + "_" + datetime.now().strftime("%H%M%S"),
            group_name=task.name,
            start_time=result.start_time or datetime.now().isoformat(),
            end_time=result.end_time,
            status=result.status,
            trigger="manual",
        )
        record.results.append(result)
        self.storage.save_execution(record)
