import pytest
import asyncio
import time
import psutil
import os
from sandbox.core.sandbox import Sandbox, SandboxError, ResourceLimitExceeded
from sandbox.config.settings import SandboxSettings

def test_basic_execution():
    """测试基本执行功能"""
    sandbox = Sandbox()
    result = sandbox.execute("""
x = 1 + 1
__result__ = x
""")
    assert result == 2

def test_memory_limit():
    """测试内存限制功能"""
    settings = SandboxSettings(max_memory_mb=10)  # 限制内存使用为10MB
    sandbox = Sandbox(settings)
    
    with pytest.raises(ResourceLimitExceeded):
        # 创建一个占用大量内存的列表
        sandbox.execute("""
import array
arr = array.array('i', [0] * 10000000)
__result__ = len(arr)
""")

def test_cpu_limit():
    """测试CPU限制功能"""
    settings = SandboxSettings(max_cpu_percent=10)  # 限制CPU使用率为10%
    sandbox = Sandbox(settings)
    
    with pytest.raises(ResourceLimitExceeded):
        # 执行一个CPU密集型操作
        sandbox.execute("""
while True:
    pass
""")

def test_time_limit():
    """测试执行时间限制"""
    settings = SandboxSettings(max_execution_time=1)  # 限制执行时间为1秒
    sandbox = Sandbox(settings)
    
    with pytest.raises(ResourceLimitExceeded):
        sandbox.execute("""
import time
time.sleep(2)  # 休眠2秒
__result__ = "完成"
""")

def test_file_access():
    """测试文件访问控制"""
    settings = SandboxSettings(
        allowed_directories=["./"],
        allow_file_operations=True
    )
    sandbox = Sandbox(settings)
    
    # 测试允许的文件操作
    result = sandbox.execute("""
with open('test.txt', 'w') as f:
    f.write('test')
__result__ = True
""")
    assert result is True
    
    # 测试不允许的文件操作
    settings.allowed_directories = []
    sandbox.update_settings(settings)
    with pytest.raises(SandboxError):
        sandbox.execute("""
with open('test.txt', 'w') as f:
    f.write('test')
__result__ = True
""")

def test_network_access():
    """测试网络访问控制"""
    settings = SandboxSettings(network_access=False)
    sandbox = Sandbox(settings)
    
    with pytest.raises(SandboxError):
        sandbox.execute("""
import urllib.request
urllib.request.urlopen('http://example.com')
__result__ = True
""")

def test_module_import():
    """测试模块导入控制"""
    settings = SandboxSettings(
        allow_imports=True,
        allowed_modules=['math', 'random']
    )
    sandbox = Sandbox(settings)
    
    # 测试允许的模块导入
    result = sandbox.execute("""
import math
__result__ = math.sqrt(16)
""")
    assert result == 4.0
    
    # 测试不允许的模块导入
    with pytest.raises(SandboxError):
        sandbox.execute("""
import os
__result__ = os.listdir('.')
""")

@pytest.mark.asyncio
async def test_async_execution():
    """测试异步执行功能"""
    sandbox = Sandbox()
    result = await sandbox.execute_async("""
import time
time.sleep(1)
__result__ = "异步执行完成"
""")
    assert result == "异步执行完成"

def test_error_handling():
    """测试错误处理"""
    sandbox = Sandbox()
    
    # 测试语法错误
    with pytest.raises(SandboxError):
        sandbox.execute("invalid syntax")
    
    # 测试运行时错误
    with pytest.raises(SandboxError):
        sandbox.execute("""
x = 1 / 0
__result__ = x
""") 