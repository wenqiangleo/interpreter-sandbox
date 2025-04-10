"""
Open Interpreter 集成接口
"""

from interpreter import interpreter
from sandbox.core.sandbox import Sandbox
from sandbox.config.settings import SandboxSettings
from sandbox.exceptions import SandboxError, ResourceLimitExceeded, SecurityError
from typing import Any, Dict, Optional, List
import os

class InterpreterSandbox:
    """Open Interpreter 沙箱集成类"""
    
    def __init__(self, settings: Optional[SandboxSettings] = None):
        """初始化沙箱"""
        # 初始化沙箱设置
        self.settings = settings or SandboxSettings()
        self.sandbox = Sandbox(self.settings)
        
        # 配置 Open Interpreter
        self._configure_interpreter()
        
        # 设置回调函数
        self._setup_callbacks()
        
        print("Sandbox initialized")
    
    def _configure_interpreter(self):
        """配置 Open Interpreter"""
        # 存储原始系统消息
        self.original_system_message = interpreter.system_message if hasattr(interpreter, "system_message") else None
        
        # 配置 LLM - 注意添加openai/前缀
        interpreter.llm.model = f"openai/{os.getenv('INTERPRETER_MODEL', 'qwq-plus')}"
        interpreter.llm.api_base = os.getenv('INTERPRETER_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        interpreter.llm.api_key = os.getenv('INTERPRETER_API_KEY', 'sk-bc4339fe8e8e48f6b57fab86b5d70afa')
        
        # 添加环境变量设置
        os.environ['OPENAI_API_KEY'] = os.getenv('INTERPRETER_API_KEY', 'sk-bc4339fe8e8e48f6b57fab86b5d70afa')
        
        # 配置运行设置
        if hasattr(interpreter, "auto_run"):
            interpreter.auto_run = True
            
        # 为了兼容性，确保设置context_window和max_tokens
        if hasattr(interpreter.llm, "context_window"):
            interpreter.llm.context_window = 8000
        if hasattr(interpreter.llm, "max_tokens"):
            interpreter.llm.max_tokens = 2000
    
    def _setup_callbacks(self):
        """设置回调函数"""
        # 设置代码执行前的回调
        interpreter.before_execution = self._before_execute
        
        # 设置代码执行后的回调
        interpreter.after_execution = self._after_execute
    
    def update_settings(self, settings: SandboxSettings) -> None:
        """更新沙箱设置"""
        self.settings = settings
        self.sandbox.update_settings(settings)
        
        # 更新系统消息
        if hasattr(interpreter, "system_message"):
            interpreter.system_message += f"""
            沙箱限制:
            - 内存使用限制: {self.settings.max_memory_mb}MB
            - CPU使用限制: {self.settings.max_cpu_percent}%
            - 执行时间限制: {self.settings.max_execution_time}秒
            - 文件系统访问: {'允许' if self.settings.allow_file_operations else '禁止'}
            - 网络访问: {'允许' if self.settings.network_access else '禁止'}
            - 允许导入的模块: {', '.join(self.settings.allowed_modules)}
            """
    
    def is_path_allowed(self, path: str) -> bool:
        """检查路径是否允许访问"""
        return self.sandbox.is_path_allowed(path)
    
    def allow_network_access(self) -> bool:
        """检查是否允许网络访问"""
        return self.settings.network_access
    
    def allow_file_operations(self) -> bool:
        """检查是否允许文件操作"""
        return self.settings.allow_file_operations
    
    def _before_execute(self, code: str) -> str:
        """代码执行前的回调"""
        # 检查路径访问权限
        if not self.sandbox.is_path_allowed('.'):
            raise SecurityError("当前目录访问被禁止")
        
        # 检查网络访问权限
        if not self.sandbox.allow_network_access():
            raise SecurityError("网络访问被禁止")
        
        # 检查文件操作权限
        if not self.sandbox.allow_file_operations():
            raise SecurityError("文件操作被禁止")
            
        return code
    
    def _after_execute(self, result: Any) -> Any:
        """代码执行后的回调"""
        # 检查资源使用情况
        if not self.sandbox.check_resources():
            raise ResourceLimitExceeded("资源使用超出限制")
            
        return result
    
    def chat(self, message: str, display=False) -> Dict[str, Any]:
        """使用 Open Interpreter 执行聊天"""
        try:
            # 重置对话历史（如果需要）
            # interpreter.messages = []
            
            # 执行聊天
            result = interpreter.chat(message, display=display)
            return {
                'type': 'success',
                'result': result
            }
        except ResourceLimitExceeded as e:
            return {
                'type': 'error',
                'error': 'ResourceLimitExceeded',
                'message': str(e)
            }
        except SandboxError as e:
            return {
                'type': 'error',
                'error': 'SandboxError',
                'message': str(e)
            }
        except Exception as e:
            return {
                'type': 'error',
                'error': type(e).__name__,
                'message': str(e)
            }
    
    def cleanup(self) -> None:
        """清理资源"""
        # 还原系统消息
        if self.original_system_message is not None and hasattr(interpreter, "system_message"):
            interpreter.system_message = self.original_system_message
        
        # 清除回调
        interpreter.before_execution = None
        interpreter.after_execution = None
        
        # 重置消息历史
        interpreter.messages = []
        
        # 清理沙箱资源
        self.sandbox.cleanup()