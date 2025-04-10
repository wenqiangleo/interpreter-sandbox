import unittest
import pytest
from sandbox.core.sandbox import Sandbox
from sandbox.config.settings import SandboxSettings
from sandbox.exceptions import SandboxError, ResourceLimitExceeded

class TestSandbox(unittest.TestCase):
    def setUp(self):
        # 创建一个允许time和array模块的沙箱设置
        self.sandbox = Sandbox(SandboxSettings(
            max_memory_mb=10,
            max_execution_time=1,
            allowed_modules=['time', 'array', 'math', 'random', 'json']
        ))
    
    def test_basic_execution(self):
        """测试基本执行功能"""
        result = self.sandbox.execute("""
x = 1 + 1
__result__ = x
""")
        self.assertEqual(result, 2)
    
    def test_memory_limit(self):
        """测试内存限制功能"""
        code = """
import array
# 尝试分配11MB内存
arr = array.array('i', [0] * (11 * 1024 * 1024 // 4))
__result__ = len(arr)
"""
        with self.assertRaises(ResourceLimitExceeded):
            self.sandbox.execute(code)
    
    def test_execution_timeout(self):
        """测试执行时间限制"""
        code = """
import time
time.sleep(2)  # 睡眠2秒，超过设置的1秒限制
__result__ = "完成"
"""
        with self.assertRaises(ResourceLimitExceeded):
            self.sandbox.execute(code)
    
    def test_forbidden_import(self):
        """测试不允许的模块导入"""
        code = """
import os  # 默认不允许导入os模块
__result__ = "导入成功"
"""
        with self.assertRaises(SandboxError):
            self.sandbox.execute(code)
    
    def test_file_access_control(self):
        """测试文件访问控制"""
        # 允许文件操作的沙箱
        file_sandbox = Sandbox(SandboxSettings(
            allowed_directories=["./"],
            allow_file_operations=True
        ))
        
        # 测试允许的文件操作
        with open('test_temp.txt', 'w') as f:
            f.write('测试文件')
        
        result = file_sandbox.execute("""
with open('test_temp.txt', 'r') as f:
    content = f.read()
__result__ = content
""")
        self.assertEqual(result, '测试文件')
        
        # 测试不允许的文件操作
        restricted_sandbox = Sandbox(SandboxSettings(
            allowed_directories=[],
            allow_file_operations=False
        ))
        
        with self.assertRaises(SandboxError):
            restricted_sandbox.execute("""
with open('test_temp.txt', 'r') as f:
    content = f.read()
__result__ = content
""")
        
        # 清理临时文件
        import os
        if os.path.exists('test_temp.txt'):
            os.remove('test_temp.txt')
    
    def test_network_access(self):
        """测试网络访问控制"""
        # 禁止网络访问的沙箱
        network_sandbox = Sandbox(SandboxSettings(
            network_access=False,
            allowed_modules=['socket', 'urllib']
        ))
        
        with self.assertRaises(SandboxError):
            network_sandbox.execute("""
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
__result__ = s.connect(("example.com", 80))
""")