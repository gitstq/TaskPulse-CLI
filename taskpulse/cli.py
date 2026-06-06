#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令行入口
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from . import __version__
from .config import Config
from .models import Task, TaskGroup, TaskType, TaskStatus, ExecutionRecord
from .executor import TaskExecutor
from .scheduler import TaskScheduler
from .storage import TaskStorage
from .tui import TaskPulseTUI
from .ai_helper import AIHelper
from .logger import get_logger, LogManager

console = Console()
logger = get_logger(__name__)

# 全局配置
config = Config()
storage = TaskStorage(
    tasks_file=config.tasks_file,
    history_dir=config.history_dir,
)
executor = TaskExecutor(max_workers=config.get("scheduler.max_concurrent", 5))
scheduler = TaskScheduler(
    executor=executor,
    check_interval=config.get("scheduler.check_interval", 1),
)


@click.group()
@click.version_option(version=__version__, prog_name="taskpulse")
@click.option("--config", "-c", help="配置文件路径")
@click.pass_context
def cli(ctx, config):
    """🚀 TaskPulse-CLI - 终端智能任务调度器"""
    ctx.ensure_object(dict)
    if config:
        ctx.obj["config"] = Config(config)


@cli.command()
@click.option("--name", "-n", required=True, help="任务名称")
@click.option("--command", "-cmd", required=True, help="执行命令")
@click.option("--type", "-t", "task_type", default="shell",
              type=click.Choice(["shell", "python", "http", "delay", "notification"]),
              help="任务类型")
@click.option("--description", "-d", default="", help="任务描述")
@click.option("--cron", "-c", default=None, help="Cron 表达式 (例如: '0 9 * * *')")
@click.option("--depends-on", "-dep", multiple=True, help="依赖任务ID")
@click.option("--timeout", default=300, help="超时时间(秒)")
@click.option("--retries", default=0, help="重试次数")
@click.option("--working-dir", "-wd", default=None, help="工作目录")
@click.option("--tag", "-tg", multiple=True, help="标签")
@click.option("--env", "-e", multiple=True, help="环境变量 (KEY=VALUE)")
def add(name, command, task_type, description, cron, depends_on, timeout, retries, working_dir, tag, env):
    """➕ 添加新任务"""
    env_dict = {}
    for e in env:
        if "=" in e:
            k, v = e.split("=", 1)
            env_dict[k] = v

    task = Task(
        name=name,
        command=command,
        task_type=TaskType(task_type),
        description=description,
        cron=cron,
        depends_on=list(depends_on),
        timeout=timeout,
        retries=retries,
        working_dir=working_dir,
        tags=list(tag),
        env=env_dict,
    )

    tasks = storage.load_tasks()
    tasks.append(task)
    storage.save_tasks(tasks)

    console.print(f"[green]✅ 任务 '{name}' 添加成功 (ID: {task.id})[/green]")

    if cron:
        scheduler.add_task(task)
        console.print(f"[cyan]📅 已注册定时调度: {cron}[/cyan]")


@cli.command()
@click.argument("task_id")
def remove(task_id):
    """🗑️  删除任务"""
    tasks = storage.load_tasks()
    task = next((t for t in tasks if t.id == task_id), None)

    if not task:
        console.print(f"[red]❌ 未找到任务: {task_id}[/red]")
        return

    tasks.remove(task)
    storage.save_tasks(tasks)
    scheduler.remove_task(task_id)
    console.print(f"[green]✅ 任务 '{task.name}' 已删除[/green]")


@cli.command()
def list():
    """📋 列出所有任务"""
    tasks = storage.load_tasks()
    groups = storage.load_groups()

    if not tasks and not groups:
        console.print("[yellow]⚠️  暂无任务[/yellow]")
        return

    # 显示任务组
    if groups:
        console.print("\n[bold cyan]📁 任务组[/bold cyan]\n")
        for group in groups:
            status = "🟢" if group.enabled else "🔴"
            console.print(f"{status} [bold]{group.name}[/bold] ({len(group.tasks)} 个任务)")
            if group.description:
                console.print(f"   [dim]{group.description}[/dim]")

    # 显示任务表格
    if tasks:
        table = Table(
            title="📋 任务列表",
            header_style="bold white on blue",
        )
        table.add_column("ID", style="dim", width=8)
        table.add_column("名称", style="cyan")
        table.add_column("类型", style="green")
        table.add_column("状态", style="yellow")
        table.add_column("定时", style="magenta")
        table.add_column("描述")

        for task in tasks:
            status = "🟢 启用" if task.enabled else "🔴 禁用"
            cron_str = task.cron or "-"
            table.add_row(
                task.id,
                task.name,
                task.task_type.value,
                status,
                cron_str,
                task.description[:30] + "..." if len(task.description) > 30 else task.description,
            )

        console.print(table)
        console.print(f"\n[dim]共 {len(tasks)} 个任务[/dim]")


@cli.command()
@click.argument("task_id", required=False)
def run(task_id):
    """▶️  执行任务"""
    tui = TaskPulseTUI(storage, executor, scheduler)
    tui.run_task_interactive(task_id)


@cli.command()
@click.option("--group", "-g", help="任务组名称")
def run_all(group):
    """▶️  执行所有任务"""
    tasks = storage.load_tasks()

    if group:
        groups = storage.load_groups()
        group_obj = next((g for g in groups if g.name == group), None)
        if group_obj:
            tasks = group_obj.tasks
            parallel = group_obj.parallel
        else:
            console.print(f"[red]❌ 未找到任务组: {group}[/red]")
            return
    else:
        parallel = False

    if not tasks:
        console.print("[yellow]⚠️  没有可执行的任务[/yellow]")
        return

    console.print(f"\n[bold cyan]🚀 开始执行 {len(tasks)} 个任务[/bold cyan]\n")

    execution_id = str(uuid.uuid4())[:8]
    record = ExecutionRecord(
        execution_id=execution_id,
        group_name=group or "default",
        start_time=datetime.now().isoformat(),
        status=TaskStatus.RUNNING,
        trigger="manual",
    )

    results = executor.execute_group(tasks, parallel=parallel)
    record.results = results
    record.end_time = datetime.now().isoformat()
    record.status = TaskStatus.SUCCESS if all(r.status == TaskStatus.SUCCESS for r in results) else TaskStatus.FAILED

    storage.save_execution(record)

    # 显示结果摘要
    success_count = sum(1 for r in results if r.status == TaskStatus.SUCCESS)
    failed_count = len(results) - success_count

    console.print(f"\n[bold]📊 执行结果:[/bold]")
    console.print(f"  ✅ 成功: {success_count}")
    console.print(f"  ❌ 失败: {failed_count}")
    console.print(f"  ⏱️  总耗时: {sum(r.duration for r in results):.2f}s")

    if failed_count > 0:
        console.print("\n[red]失败的任务:[/red]")
        for r in results:
            if r.status != TaskStatus.SUCCESS:
                console.print(f"  - {r.task_name}: {r.error_message}")


@cli.command()
def monitor():
    """📺 启动监控界面"""
    tui = TaskPulseTUI(storage, executor, scheduler)
    tui.run()


@cli.command()
@click.option("--daemon", "-d", is_flag=True, help="后台运行")
def start(daemon):
    """▶️  启动调度器"""
    if scheduler.is_running():
        console.print("[yellow]⚠️  调度器已在运行中[/yellow]")
        return

    tasks = storage.load_tasks()
    for task in tasks:
        if task.cron and task.enabled:
            scheduler.add_task(task)

    scheduler.start()
    console.print("[green]✅ 调度器已启动[/green]")
    console.print(f"[dim]已注册 {len([t for t in tasks if t.cron and t.enabled])} 个定时任务[/dim]")

    if not daemon:
        try:
            console.print("\n[dim]按 Ctrl+C 停止调度器[/dim]\n")
            import time
            while scheduler.is_running():
                time.sleep(1)
        except KeyboardInterrupt:
            scheduler.stop()
            console.print("\n[yellow]🛑 调度器已停止[/yellow]")


@cli.command()
def stop():
    """🛑 停止调度器"""
    if not scheduler.is_running():
        console.print("[yellow]⚠️  调度器未在运行[/yellow]")
        return

    scheduler.stop()
    console.print("[green]✅ 调度器已停止[/green]")


@cli.command()
def status():
    """📊 查看状态"""
    scheduler_status = "🟢 运行中" if scheduler.is_running() else "🔴 已停止"
    tasks = storage.load_tasks()
    stats = storage.get_task_stats()

    content = Text()
    content.append(f"调度器状态: {scheduler_status}\n", style="bold")
    content.append(f"任务总数: {len(tasks)}\n")
    content.append(f"定时任务: {len([t for t in tasks if t.cron])}\n")
    content.append(f"总执行次数: {stats.get('total_executions', 0)}\n")
    content.append(f"成功次数: {stats.get('success_count', 0)}\n")
    content.append(f"失败次数: {stats.get('failed_count', 0)}\n")
    content.append(f"成功率: {stats.get('success_rate', 'N/A')}\n")

    panel = Panel(content, title="📊 系统状态", border_style="green")
    console.print(panel)


@cli.command()
@click.option("--limit", "-n", default=20, help="显示条数")
def history(limit):
    """📜 查看执行历史"""
    executions = storage.load_executions(limit=limit)

    if not executions:
        console.print("[yellow]⚠️  暂无执行记录[/yellow]")
        return

    table = Table(
        title=f"📜 最近 {len(executions)} 条执行记录",
        header_style="bold white on blue",
    )
    table.add_column("执行ID", style="dim")
    table.add_column("任务组", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("触发", style="magenta")
    table.add_column("开始时间", style="white")
    table.add_column("耗时", style="yellow")

    for exec_record in executions:
        status_color = "green" if exec_record.status == TaskStatus.SUCCESS else "red"
        duration = ""
        if exec_record.end_time and exec_record.start_time:
            try:
                start = datetime.fromisoformat(exec_record.start_time)
                end = datetime.fromisoformat(exec_record.end_time)
                duration = f"{(end - start).total_seconds():.1f}s"
            except:
                duration = "-"

        table.add_row(
            exec_record.execution_id,
            exec_record.group_name,
            f"[{status_color}]{exec_record.status.value}[/{status_color}]",
            exec_record.trigger,
            exec_record.start_time[:19] if exec_record.start_time else "-",
            duration,
        )

    console.print(table)


@cli.command()
@click.argument("description")
@click.option("--type", "task_type", default="shell",
              type=click.Choice(["shell", "python"]),
              help="任务类型")
def ai_generate(description, task_type):
    """🤖 AI 生成任务脚本"""
    ai = AIHelper(
        provider=config.get("ai.provider", "openai"),
        api_key=config.get("ai.api_key", ""),
        api_base=config.get("ai.api_base", ""),
        model=config.get("ai.model", "gpt-3.5-turbo"),
    )

    if not ai.is_available():
        console.print("[yellow]⚠️  未配置 AI API Key，请先配置:[/yellow]")
        console.print("  taskpulse config set ai.api_key YOUR_API_KEY")
        return

    console.print(f"[cyan]🤖 正在使用 AI 生成 {task_type} 脚本...[/cyan]")

    with console.status("[bold green]AI 思考中..."):
        script = ai.generate_task_script(description, task_type)

    if script:
        console.print(f"\n[bold green]✅ 生成成功![/bold green]\n")
        console.print(Panel(script, title="📝 生成的脚本", border_style="green"))

        if click.confirm("\n是否保存为任务?"):
            name = click.prompt("任务名称")
            task = Task(
                name=name,
                command=script,
                task_type=TaskType(task_type),
                description=description,
            )
            tasks = storage.load_tasks()
            tasks.append(task)
            storage.save_tasks(tasks)
            console.print(f"[green]✅ 任务 '{name}' 已保存[/green]")
    else:
        console.print("[red]❌ 生成失败[/red]")


@cli.command()
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """⚙️ 设置配置项"""
    config.set(key, value)
    console.print(f"[green]✅ 配置已更新: {key} = {value}[/green]")


@cli.command()
@click.argument("key")
def config_get(key):
    """🔍 获取配置项"""
    value = config.get(key)
    if value is not None:
        console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]")
    else:
        console.print(f"[yellow]⚠️  配置项不存在: {key}[/yellow]")


@cli.command()
def init():
    """🚀 初始化项目"""
    if os.path.exists("tasks.yaml"):
        console.print("[yellow]⚠️  项目已初始化[/yellow]")
        return

    # 创建示例任务文件
    example = {
        "version": "1.0",
        "updated_at": datetime.now().isoformat(),
        "groups": [
            {
                "name": "示例任务组",
                "description": "TaskPulse 示例任务",
                "parallel": False,
                "tasks": [
                    {
                        "name": "问候任务",
                        "command": "echo 'Hello, TaskPulse!'",
                        "task_type": "shell",
                        "description": "简单的问候任务",
                    },
                    {
                        "name": "系统信息",
                        "command": "uname -a",
                        "task_type": "shell",
                        "description": "显示系统信息",
                    },
                ],
            }
        ],
    }

    with open("tasks.yaml", "w", encoding="utf-8") as f:
        import yaml
        yaml.dump(example, f, default_flow_style=False, allow_unicode=True)

    console.print("[green]✅ 项目初始化完成![/green]")
    console.print("[dim]已创建 tasks.yaml 示例文件[/dim]")
    console.print("\n[bold]快速开始:[/bold]")
    console.print("  taskpulse list       # 查看任务")
    console.print("  taskpulse run        # 运行任务")
    console.print("  taskpulse monitor    # 启动监控")


@cli.command()
def logs():
    """📄 查看日志"""
    log_manager = LogManager(config.logs_dir)
    log_files = log_manager.get_log_files()

    if not log_files:
        console.print("[yellow]⚠️  暂无日志文件[/yellow]")
        return

    console.print(f"\n[bold]📁 日志文件 ({len(log_files)} 个):[/bold]\n")
    for i, filename in enumerate(log_files[:10]):
        console.print(f"  [{i+1}] {filename}")

    try:
        choice = int(console.input("\n选择要查看的日志 (编号): ")) - 1
        if 0 <= choice < len(log_files):
            content = log_manager.read_log(log_files[choice], lines=50)
            console.print(Panel(content, title=f"📄 {log_files[choice]}", border_style="blue"))
        else:
            console.print("[red]❌ 无效选择[/red]")
    except ValueError:
        console.print("[red]❌ 请输入数字[/red]")


def main():
    """主入口"""
    cli()


if __name__ == "__main__":
    main()
