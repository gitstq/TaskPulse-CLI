#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 辅助模块
"""

import json
from typing import Optional, Dict, Any

import requests

from .logger import get_logger

logger = get_logger(__name__)


class AIHelper:
    """AI 辅助助手"""

    def __init__(
        self,
        provider: str = "openai",
        api_key: str = "",
        api_base: str = "",
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ):
        self.provider = provider.lower()
        self.api_key = api_key
        self.api_base = api_base or self._get_default_base()
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _get_default_base(self) -> str:
        """获取默认 API 地址"""
        defaults = {
            "openai": "https://api.openai.com/v1",
            "glm": "https://open.bigmodel.cn/api/paas/v4",
            "claude": "https://api.anthropic.com/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1",
        }
        return defaults.get(self.provider, "https://api.openai.com/v1")

    def generate_task_script(self, description: str, task_type: str = "shell") -> Optional[str]:
        """根据描述生成任务脚本"""
        if not self.api_key:
            logger.warning("⚠️  未配置 API Key，无法使用 AI 功能")
            return None

        prompt = f"""你是一个专业的开发任务脚本生成助手。
请根据以下描述生成一个 {task_type} 类型的任务脚本：

描述：{description}

要求：
1. 脚本应该简洁、高效、可执行
2. 如果是 shell 脚本，使用 bash 语法
3. 如果是 python 脚本，使用标准库
4. 添加必要的错误处理
5. 只返回脚本内容，不要添加解释

脚本："""

        try:
            response = self._call_api(prompt)
            if response:
                # 清理响应内容
                script = response.strip()
                if script.startswith("```"):
                    lines = script.split("\n")
                    # 去掉第一行和最后一行
                    if len(lines) > 2:
                        script = "\n".join(lines[1:-1])
                return script.strip()
        except Exception as e:
            logger.error(f"❌ AI 生成失败: {e}")

        return None

    def explain_task(self, command: str, task_type: str = "shell") -> Optional[str]:
        """解释任务脚本"""
        if not self.api_key:
            return None

        prompt = f"""请解释以下 {task_type} 任务脚本的功能和每一步的作用：

```
{command}
```

请用中文简要说明："""

        try:
            return self._call_api(prompt)
        except Exception as e:
            logger.error(f"❌ AI 解释失败: {e}")
            return None

    def suggest_tasks(self, project_description: str) -> Optional[list]:
        """根据项目描述建议任务列表"""
        if not self.api_key:
            return None

        prompt = f"""根据以下项目描述，建议一个自动化任务列表（YAML格式）：

项目描述：{project_description}

请返回一个 JSON 数组，每个元素包含：
- name: 任务名称
- command: 任务命令
- type: 任务类型 (shell/python/http/delay/notification)
- description: 任务描述
- cron: 可选的定时表达式

只返回 JSON 数组，不要添加其他内容。"""

        try:
            response = self._call_api(prompt)
            if response:
                # 提取 JSON 部分
                start = response.find("[")
                end = response.rfind("]")
                if start != -1 and end != -1:
                    return json.loads(response[start:end+1])
        except Exception as e:
            logger.error(f"❌ AI 建议生成失败: {e}")

        return None

    def _call_api(self, prompt: str) -> Optional[str]:
        """调用 AI API"""
        if self.provider == "openai" or self.provider == "glm":
            return self._call_openai_compatible(prompt)
        elif self.provider == "claude":
            return self._call_claude(prompt)
        else:
            return self._call_openai_compatible(prompt)

    def _call_openai_compatible(self, prompt: str) -> Optional[str]:
        """调用 OpenAI 兼容 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _call_claude(self, prompt: str) -> Optional[str]:
        """调用 Claude API"""
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
        }

        response = requests.post(
            f"{self.api_base}/messages",
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()

        result = response.json()
        return result["content"][0]["text"]

    def is_available(self) -> bool:
        """检查 AI 是否可用"""
        return bool(self.api_key)
