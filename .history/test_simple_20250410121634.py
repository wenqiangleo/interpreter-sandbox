# 创建文件 test_simple.py
from sandbox.core.sandbox import Sandbox
from sandbox.config.settings import SandboxSettings

# 创建沙箱实例
sandbox = Sandbox(SandboxSettings(
    max_memory_mb=100,
    max_execution_time=5,
    allowed_modules=['math', 'random']
))

# 执行代码
result = sandbox.execute("""
import math
x = math.sqrt(16)
__result__ = x
""")

print(f"执行结果: {result}")