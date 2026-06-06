#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaskPulse-CLI - 终端智能任务调度器
Setup configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="taskpulse-cli",
    version="1.0.0",
    author="TaskPulse Team",
    author_email="taskpulse@example.com",
    description="🚀 终端智能任务调度器 - 让自动化触手可及",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gitstq/TaskPulse-CLI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "rich>=13.0.0",
        "schedule>=1.2.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "taskpulse=taskpulse.cli:main",
            "tp=taskpulse.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
