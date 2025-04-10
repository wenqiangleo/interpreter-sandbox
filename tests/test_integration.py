import unittest
from sandbox.integration.interpreter import InterpreterSandbox
from sandbox.config.settings import SandboxSettings
import os

class TestInterpreterIntegration(unittest.TestCase):
    def setUp(self):
        # 设置环境变量
        os.environ['INTERPRETER_API_BASE'] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        os.environ['INTERPRETER_MODEL'] = "qwq-plus"
        os.environ['INTERPRETER_API_KEY'] = "dummy_key_for_testing"
        
        self.sandbox = InterpreterSandbox(SandboxSettings(
            max_memory_mb=100,
            max_execution_time=5,
            allowed_modules=['math']
        ))
    
    def tearDown(self):
        self.sandbox.cleanup()
    
    def test_basic_chat(self):
        """测试基本聊天功能"""
        # 由于需要真实的API密钥，这个测试可能会失败
        # 在实际环境中使用有效的API密钥
        result = self.sandbox.chat("请计算1+1等于多少")
        self.assertIn('type', result)
    
    def test_permission_checks(self):
        """测试权限检查功能"""
        self.assertTrue(self.sandbox.is_path_allowed('./'))
        self.assertFalse(self.sandbox.allow_network_access())
        
        # 更新设置
        new_settings = SandboxSettings(
            network_access=True,
            allowed_directories=['./data']
        )
        self.sandbox.update_settings(new_settings)
        
        self.assertTrue(self.sandbox.allow_network_access())
        self.assertTrue(self.sandbox.is_path_allowed('./data'))
        self.assertFalse(self.sandbox.is_path_allowed('/etc'))