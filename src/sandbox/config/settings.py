"""
沙箱配置模块
"""

from typing import List
from dataclasses import dataclass, field

@dataclass
class SandboxSettings:
    """沙箱配置"""
    max_memory_mb: int = 100  # 内存限制（MB）
    max_cpu_percent: int = 50  # CPU使用率限制（%）
    max_execution_time: int = 5  # 执行时间限制（秒）
    allowed_directories: List[str] = field(default_factory=lambda: ["./"])  # 允许访问的目录
    network_access: bool = False  # 是否允许网络访问
    allow_file_operations: bool = False  # 是否允许文件操作
    allow_imports: bool = True  # 是否允许导入模块
    allowed_modules: List[str] = field(default_factory=lambda: ['math', 'random', 'json'])  # 允许导入的模块
    check_interval: float = 0.1  # 资源检查间隔（秒）

# 默认配置
DEFAULT_SETTINGS = SandboxSettings() 