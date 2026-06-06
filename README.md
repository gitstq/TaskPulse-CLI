<div align="center">

# 🚀 TaskPulse-CLI

**终端智能任务调度器 - 让自动化触手可及**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()
[![Tests](https://img.shields.io/badge/Tests-15%20passed-brightgreen.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="简体中文"></a>
## 🎉 项目介绍

**TaskPulse-CLI** 是一款专为开发者打造的终端智能任务调度器。它让繁琐的重复性工作自动化变得简单优雅——只需一条命令，即可将日常开发中的定时任务、批处理作业、监控告警等流程编排得井井有条。

### 💡 灵感来源

在日常开发中，我们频繁遇到这样的场景：定时备份数据库、定时拉取代码、批量处理文件、定时发送报告... 现有的工具要么过于重量级（如 Jenkins），要么功能单一（如 crontab），缺乏一个**轻量、统一、可视化**的终端任务管理方案。TaskPulse-CLI 应运而生，填补了这一空白。

### ✨ 自研差异化亮点

- 🤖 **AI 辅助生成任务脚本** — 用自然语言描述需求，AI 自动生成可执行脚本
- 🖥️ **实时 TUI 监控界面** — 基于 Rich 库打造的精美终端界面，任务状态一目了然
- 🔗 **智能依赖编排** — 支持任务链式依赖，自动解析执行顺序
- 📊 **完整的执行历史追踪** — 每次执行都有记录，便于审计和排错

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 📝 **多类型任务支持** | Shell、Python、HTTP 请求、延迟等待、桌面通知 |
| ⏰ **Cron 定时调度** | 类 Unix Cron 表达式，精确控制执行时机 |
| 🔗 **任务依赖编排** | 支持 `depends_on` 链式依赖，自动拓扑排序 |
| 🖥️ **TUI 实时监控** | 基于 Rich 的终端仪表盘，实时查看任务状态 |
| 🤖 **AI 脚本生成** | 集成 OpenAI/GLM/Claude，自然语言生成任务脚本 |
| 📦 **任务组管理** | 支持串行/并行模式，灵活组织批量任务 |
| 🔔 **多通道通知** | Webhook、邮件、桌面通知，任务完成即时知晓 |
| 📊 **执行历史追踪** | 完整的执行记录与统计，成功率一目了然 |
| ⚙️ **YAML/JSON 配置** | 人类友好的配置格式，版本控制友好 |
| 🧪 **完整单元测试** | 15+ 测试用例，核心功能全覆盖 |

---

## 🚀 快速开始

### 环境要求

- **Python** >= 3.9
- **操作系统** : Linux / macOS / Windows

### 安装步骤

```bash
# 方式一：通过 pip 安装
pip install taskpulse-cli

# 方式二：从源码安装
git clone https://github.com/gitstq/TaskPulse-CLI.git
cd TaskPulse-CLI
pip install -e .
```

### 快速体验

```bash
# 初始化项目
taskpulse init

# 查看任务列表
taskpulse list

# 执行所有任务
taskpulse run-all

# 启动监控界面
taskpulse monitor

# 启动定时调度器
taskpulse start
```

---

## 📖 详细使用指南

### 1. 添加任务

```bash
# 添加一个 Shell 任务
taskpulse add \
  --name "备份数据库" \
  --command "mysqldump -u root mydb > backup.sql" \
  --type shell \
  --description "每日数据库备份" \
  --cron "0 2 * * *"

# 添加一个 Python 任务
taskpulse add \
  --name "数据分析" \
  --command "import pandas as pd; print('分析完成')" \
  --type python \
  --description "运行数据分析脚本"

# 添加 HTTP 监控任务
taskpulse add \
  --name "API健康检查" \
  --command "GET https://api.example.com/health" \
  --type http \
  --description "检查API可用性" \
  --cron "*/5 * * * *"
```

### 2. 任务配置文件示例

```yaml
version: "1.0"
updated_at: "2024-01-01T00:00:00"

groups:
  - name: "每日运维任务"
    description: "系统日常维护"
    parallel: false
    tasks:
      - name: "清理日志"
        command: "find /var/log -name '*.log' -mtime +7 -delete"
        task_type: shell
        description: "清理7天前的日志文件"
        cron: "0 3 * * *"

      - name: "备份数据库"
        command: "mysqldump -u root mydb > /backup/db_$(date +%Y%m%d).sql"
        task_type: shell
        description: "每日数据库备份"
        depends_on:
          - "清理日志"
        cron: "0 2 * * *"
        retries: 3
        retry_delay: 60

      - name: "发送报告"
        command: "python send_report.py"
        task_type: python
        description: "发送日报邮件"
        depends_on:
          - "备份数据库"
```

### 3. AI 辅助生成任务

```bash
# 使用 AI 生成任务脚本
taskpulse ai-generate "每天凌晨3点清理/tmp目录下超过1GB的文件" --type shell

# AI 会生成类似以下的脚本：
# find /tmp -type f -size +1G -mtime +1 -delete
```

### 4. 配置 AI 接口

```bash
# 设置 OpenAI API Key
taskpulse config-set ai.api_key sk-your-api-key

# 使用 GLM 模型
taskpulse config-set ai.provider glm
taskpulse config-set ai.api_key your-glm-api-key
taskpulse config-set ai.model glm-4
```

---

## 💡 设计思路与迭代规划

### 技术选型原因

| 技术 | 选型理由 |
|------|----------|
| **Python** | 跨平台、生态丰富、开发效率高 |
| **Click** | 业界标准的 CLI 框架，命令解析优雅 |
| **Rich** | 终端 UI 渲染利器，支持表格/面板/进度条 |
| **Schedule** | 轻量级定时调度，API 简洁直观 |
| **PyYAML** | 人类友好的配置格式，便于版本控制 |

### 后续迭代计划

- [ ] **v1.1.0** — 任务模板市场，一键导入常用任务
- [ ] **v1.2.0** — 分布式任务执行，支持多节点部署
- [ ] **v1.3.0** — Web 管理界面，远程管理任务
- [ ] **v2.0.0** — 插件系统，支持自定义任务类型

### 社区贡献方向

- 🌟 提交常用任务模板
- 🐛 报告 Bug 和优化建议
- 📝 完善文档和教程
- 🔌 开发自定义插件

---

## 📦 打包与部署指南

### 本地开发

```bash
# 克隆仓库
git clone https://github.com/gitstq/TaskPulse-CLI.git
cd TaskPulse-CLI

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v
```

### 打包发布

```bash
# 构建分发包
python -m build

# 上传到 PyPI
python -m twine upload dist/*
```

### 跨平台安装

```bash
# Linux/macOS
pip install taskpulse-cli

# Windows
pip install taskpulse-cli

# 或使用 pipx（推荐）
pipx install taskpulse-cli
```

---

## 🤝 贡献指南

### 提交 PR

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feat/amazing-feature`
3. 提交更改：`git commit -m 'feat: 添加 amazing 功能'`
4. 推送分支：`git push origin feat/amazing-feature`
5. 提交 Pull Request

### Issue 反馈

- 🐛 **Bug 报告**：请提供复现步骤、环境信息、错误日志
- 💡 **功能建议**：请描述使用场景和期望行为
- 📖 **文档改进**：请指出具体位置和修改建议

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

<a name="english"></a>
## 🎉 Introduction

**TaskPulse-CLI** is an intelligent terminal task scheduler built for developers. It makes automating repetitive work simple and elegant — with just one command, you can orchestrate scheduled tasks, batch jobs, monitoring alerts, and more.

### 💡 Inspiration

In daily development, we frequently encounter scenarios: scheduled database backups, code pulls, file batch processing, report generation... Existing tools are either too heavyweight (like Jenkins) or too limited (like crontab). TaskPulse-CLI fills this gap with a **lightweight, unified, visual** terminal task management solution.

### ✨ Differentiation

- 🤖 **AI-Assisted Script Generation** — Describe your needs in natural language, AI generates executable scripts
- 🖥️ **Real-time TUI Dashboard** — Beautiful terminal interface built with Rich, task status at a glance
- 🔗 **Smart Dependency Orchestration** — Chain task dependencies with automatic topological sorting
- 📊 **Complete Execution History** — Every execution is recorded for auditing and troubleshooting

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 📝 **Multi-type Tasks** | Shell, Python, HTTP requests, delay, desktop notifications |
| ⏰ **Cron Scheduling** | Unix-like Cron expressions for precise timing control |
| 🔗 **Task Dependencies** | `depends_on` chain support with auto topological sorting |
| 🖥️ **TUI Real-time Monitor** | Rich-based terminal dashboard for live task status |
| 🤖 **AI Script Generation** | Integrates OpenAI/GLM/Claude for natural language to script |
| 📦 **Task Group Management** | Serial/parallel modes for flexible batch organization |
| 🔔 **Multi-channel Notifications** | Webhook, email, desktop notifications |
| 📊 **Execution History** | Complete execution records and statistics |
| ⚙️ **YAML/JSON Config** | Human-friendly configuration format |
| 🧪 **Full Unit Tests** | 15+ test cases covering core functionality |

---

## 🚀 Quick Start

### Requirements

- **Python** >= 3.9
- **OS**: Linux / macOS / Windows

### Installation

```bash
# Method 1: via pip
pip install taskpulse-cli

# Method 2: from source
git clone https://github.com/gitstq/TaskPulse-CLI.git
cd TaskPulse-CLI
pip install -e .
```

### Quick Demo

```bash
# Initialize project
taskpulse init

# List tasks
taskpulse list

# Run all tasks
taskpulse run-all

# Start monitoring dashboard
taskpulse monitor

# Start scheduler daemon
taskpulse start
```

---

## 📖 Usage Guide

### Add a Task

```bash
# Add a shell task
taskpulse add \
  --name "backup-db" \
  --command "mysqldump -u root mydb > backup.sql" \
  --type shell \
  --description "Daily database backup" \
  --cron "0 2 * * *"

# Add a Python task
taskpulse add \
  --name "data-analysis" \
  --command "import pandas as pd; print('Done')" \
  --type python \
  --description "Run data analysis"

# Add HTTP health check
taskpulse add \
  --name "api-health" \
  --command "GET https://api.example.com/health" \
  --type http \
  --description "Check API availability" \
  --cron "*/5 * * * *"
```

### Task Configuration Example

```yaml
version: "1.0"
updated_at: "2024-01-01T00:00:00"

groups:
  - name: "Daily Ops"
    description: "System daily maintenance"
    parallel: false
    tasks:
      - name: "clean-logs"
        command: "find /var/log -name '*.log' -mtime +7 -delete"
        task_type: shell
        description: "Clean logs older than 7 days"
        cron: "0 3 * * *"

      - name: "backup-db"
        command: "mysqldump -u root mydb > /backup/db_$(date +%Y%m%d).sql"
        task_type: shell
        description: "Daily database backup"
        depends_on:
          - "clean-logs"
        cron: "0 2 * * *"
        retries: 3
        retry_delay: 60
```

### AI-Assisted Task Generation

```bash
# Generate task script with AI
taskpulse ai-generate "Clean files over 1GB in /tmp at 3AM daily" --type shell
```

### Configure AI Provider

```bash
# Set OpenAI API Key
taskpulse config-set ai.api_key sk-your-api-key

# Use GLM model
taskpulse config-set ai.provider glm
taskpulse config-set ai.api_key your-glm-api-key
taskpulse config-set ai.model glm-4
```

---

## 💡 Design & Roadmap

### Tech Stack

| Technology | Reason |
|------------|--------|
| **Python** | Cross-platform, rich ecosystem, high dev efficiency |
| **Click** | Industry-standard CLI framework |
| **Rich** | Terminal UI rendering with tables/panels/progress |
| **Schedule** | Lightweight scheduling with intuitive API |
| **PyYAML** | Human-friendly configuration format |

### Roadmap

- [ ] **v1.1.0** — Task template marketplace
- [ ] **v1.2.0** — Distributed task execution
- [ ] **v1.3.0** — Web management interface
- [ ] **v2.0.0** — Plugin system for custom task types

---

## 🤝 Contributing

### PR Process

1. Fork the repository
2. Create feature branch: `git checkout -b feat/amazing-feature`
3. Commit: `git commit -m 'feat: add amazing feature'`
4. Push: `git push origin feat/amazing-feature`
5. Open Pull Request

### Issue Reporting

- 🐛 **Bug**: Provide reproduction steps, environment, error logs
- 💡 **Feature**: Describe use case and expected behavior
- 📖 **Docs**: Point to specific location and suggested changes

---

## 📄 License

[MIT License](LICENSE)

---

<a name="繁體中文"></a>
## 🎉 專案介紹

**TaskPulse-CLI** 是一款專為開發者打造的終端智能任務調度器。它讓繁瑣的重複性工作自動化變得簡單優雅——只需一條命令，即可將日常開發中的定時任務、批處理作業、監控告警等流程編排得井井有條。

### 💡 靈感來源

在日常開發中，我們頻繁遇到這樣的場景：定時備份資料庫、定時拉取程式碼、批次處理檔案、定時發送報告... 現有的工具要么過於重量級（如 Jenkins），要么功能單一（如 crontab），缺乏一個**輕量、統一、可視化**的終端任務管理方案。TaskPulse-CLI 應運而生，填補了這一空白。

### ✨ 自研差異化亮點

- 🤖 **AI 輔助生成任務腳本** — 用自然語言描述需求，AI 自動生成可執行腳本
- 🖥️ **即時 TUI 監控介面** — 基於 Rich 庫打造的精美終端介面，任務狀態一目瞭然
- 🔗 **智能依賴編排** — 支援任務鏈式依賴，自動解析執行順序
- 📊 **完整的執行歷史追蹤** — 每次執行都有記錄，便於審計和排錯

---

## ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 📝 **多類型任務支援** | Shell、Python、HTTP 請求、延遲等待、桌面通知 |
| ⏰ **Cron 定時調度** | 類 Unix Cron 表達式，精確控制執行時機 |
| 🔗 **任務依賴編排** | 支援 `depends_on` 鏈式依賴，自動拓撲排序 |
| 🖥️ **TUI 即時監控** | 基於 Rich 的終端儀表板，即時查看任務狀態 |
| 🤖 **AI 腳本生成** | 整合 OpenAI/GLM/Claude，自然語言生成任務腳本 |
| 📦 **任務群組管理** | 支援串行/並行模式，靈活組織批次任務 |
| 🔔 **多通道通知** | Webhook、郵件、桌面通知，任務完成即時知曉 |
| 📊 **執行歷史追蹤** | 完整的執行記錄與統計，成功率一目瞭然 |
| ⚙️ **YAML/JSON 配置** | 人類友好的配置格式，版本控制友好 |
| 🧪 **完整單元測試** | 15+ 測試案例，核心功能全覆蓋 |

---

## 🚀 快速開始

### 環境要求

- **Python** >= 3.9
- **作業系統** : Linux / macOS / Windows

### 安裝步驟

```bash
# 方式一：透過 pip 安裝
pip install taskpulse-cli

# 方式二：從原始碼安裝
git clone https://github.com/gitstq/TaskPulse-CLI.git
cd TaskPulse-CLI
pip install -e .
```

### 快速體驗

```bash
# 初始化專案
taskpulse init

# 查看任務列表
taskpulse list

# 執行所有任務
taskpulse run-all

# 啟動監控介面
taskpulse monitor

# 啟動定時調度器
taskpulse start
```

---

## 📖 詳細使用指南

### 1. 添加任務

```bash
# 添加一個 Shell 任務
taskpulse add \
  --name "備份資料庫" \
  --command "mysqldump -u root mydb > backup.sql" \
  --type shell \
  --description "每日資料庫備份" \
  --cron "0 2 * * *"

# 添加一個 Python 任務
taskpulse add \
  --name "資料分析" \
  --command "import pandas as pd; print('分析完成')" \
  --type python \
  --description "執行資料分析腳本"

# 添加 HTTP 監控任務
taskpulse add \
  --name "API健康檢查" \
  --command "GET https://api.example.com/health" \
  --type http \
  --description "檢查API可用性" \
  --cron "*/5 * * * *"
```

### 2. 任務配置檔案範例

```yaml
version: "1.0"
updated_at: "2024-01-01T00:00:00"

groups:
  - name: "每日維運任務"
    description: "系統日常維護"
    parallel: false
    tasks:
      - name: "清理日誌"
        command: "find /var/log -name '*.log' -mtime +7 -delete"
        task_type: shell
        description: "清理7天前的日誌檔案"
        cron: "0 3 * * *"

      - name: "備份資料庫"
        command: "mysqldump -u root mydb > /backup/db_$(date +%Y%m%d).sql"
        task_type: shell
        description: "每日資料庫備份"
        depends_on:
          - "清理日誌"
        cron: "0 2 * * *"
        retries: 3
        retry_delay: 60
```

### 3. AI 輔助生成任務

```bash
# 使用 AI 生成任務腳本
taskpulse ai-generate "每天凌晨3點清理/tmp目錄下超過1GB的檔案" --type shell
```

### 4. 配置 AI 介面

```bash
# 設定 OpenAI API Key
taskpulse config-set ai.api_key sk-your-api-key

# 使用 GLM 模型
taskpulse config-set ai.provider glm
taskpulse config-set ai.api_key your-glm-api-key
taskpulse config-set ai.model glm-4
```

---

## 💡 設計思路與迭代規劃

### 技術選型原因

| 技術 | 選型理由 |
|------|----------|
| **Python** | 跨平台、生態豐富、開發效率高 |
| **Click** | 業界標準的 CLI 框架，命令解析優雅 |
| **Rich** | 終端 UI 渲染利器，支援表格/面板/進度條 |
| **Schedule** | 輕量級定時調度，API 簡潔直觀 |
| **PyYAML** | 人類友好的配置格式，便於版本控制 |

### 後續迭代計劃

- [ ] **v1.1.0** — 任務模板市場，一鍵匯入常用任務
- [ ] **v1.2.0** — 分散式任務執行，支援多節點部署
- [ ] **v1.3.0** — Web 管理介面，遠端管理任務
- [ ] **v2.0.0** — 插件系統，支援自定義任務類型

---

## 🤝 貢獻指南

### 提交 PR

1. Fork 本倉庫
2. 建立功能分支：`git checkout -b feat/amazing-feature`
3. 提交更改：`git commit -m 'feat: 新增 amazing 功能'`
4. 推送分支：`git push origin feat/amazing-feature`
5. 提交 Pull Request

---

## 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

<div align="center">

**Made with ❤️ by TaskPulse Team**

⭐ Star us on GitHub — it motivates us a lot!

</div>
