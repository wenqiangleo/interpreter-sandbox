"""
Open Interpreter 安全沙箱模块
提供安全的代码执行环境，限制资源访问和使用
"""

import os
import sys
import time
import psutil
import threading
import traceback
from contextlib import contextmanager
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from sandbox.config.settings import SandboxSettings, DEFAULT_SETTINGS
from sandbox.exceptions import SandboxError, ResourceLimitExceeded, SecurityError

class Sandbox:
    """沙箱环境类"""
    
    def __init__(self, settings: Optional[SandboxSettings] = None):
        """初始化沙箱
        
        Args:
            settings: 沙箱配置，如果为 None 则使用默认配置
        """
        self.settings = settings or SandboxSettings()
        self._process = None
        self._monitor_thread = None
        self._stop_monitor = threading.Event()
        self._start_time = None
        self._globals = self._setup_globals()
        print("Sandbox initialized")  # 调试信息
    
    def _setup_globals(self) -> Dict[str, Any]:
        """设置全局变量
        
        Returns:
            Dict[str, Any]: 全局变量字典
        """
        # 定义不安全的模块列表
        unsafe_modules = [
            'os', 'sys', 'subprocess', 'socket', 'shutil', 'glob',
            'tempfile', 'pickle', 'marshal', 'ctypes', 'signal',
            'threading', 'multiprocessing', 'asyncio', 'select',
            'fcntl', 'termios', 'tty', 'pty', 'pwd', 'grp', 'crypt',
            'spwd', 'resource', 'mmap', 'fcntl', 'termios', 'tty',
            'pty', 'pwd', 'grp', 'crypt', 'spwd', 'resource', 'mmap'
        ]
        
        # 设置安全的全局变量
        globals_dict = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'frozenset': frozenset,
                'type': type,
                'isinstance': isinstance,
                'issubclass': issubclass,
                'hasattr': hasattr,
                'getattr': getattr,
                'setattr': setattr,
                'delattr': delattr,
                'property': property,
                'staticmethod': staticmethod,
                'classmethod': classmethod,
                'super': super,
                'object': object,
                'Exception': Exception,
                'ValueError': ValueError,
                'TypeError': TypeError,
                'AttributeError': AttributeError,
                'KeyError': KeyError,
                'IndexError': IndexError,
                'StopIteration': StopIteration,
                'AssertionError': AssertionError,
                'NotImplementedError': NotImplementedError,
                'ImportError': ImportError,
                'NameError': NameError,
                'UnboundLocalError': UnboundLocalError,
                'RuntimeError': RuntimeError,
                'SyntaxError': SyntaxError,
                'IndentationError': IndentationError,
                'TabError': TabError,
                'SystemError': SystemError,
                'ReferenceError': ReferenceError,
                'MemoryError': MemoryError,
                'BufferError': BufferError,
                'Warning': Warning,
                'UserWarning': UserWarning,
                'DeprecationWarning': DeprecationWarning,
                'PendingDeprecationWarning': PendingDeprecationWarning,
                'SyntaxWarning': SyntaxWarning,
                'RuntimeWarning': RuntimeWarning,
                'FutureWarning': FutureWarning,
                'ImportWarning': ImportWarning,
                'UnicodeWarning': UnicodeWarning,
                'BytesWarning': BytesWarning,
                'ResourceWarning': ResourceWarning,
                'abs': abs,
                'all': all,
                'any': any,
                'bin': bin,
                'bool': bool,
                'chr': chr,
                'complex': complex,
                'divmod': divmod,
                'enumerate': enumerate,
                'filter': filter,
                'format': format,
                'frozenset': frozenset,
                'hash': hash,
                'hex': hex,
                'id': id,
                'input': input,
                'isinstance': isinstance,
                'issubclass': issubclass,
                'iter': iter,
                'len': len,
                'list': list,
                'map': map,
                'max': max,
                'min': min,
                'next': next,
                'oct': oct,
                'ord': ord,
                'pow': pow,
                'print': print,
                'range': range,
                'repr': repr,
                'reversed': reversed,
                'round': round,
                'set': set,
                'slice': slice,
                'sorted': sorted,
                'str': str,
                'sum': sum,
                'tuple': tuple,
                'type': type,
                'zip': zip,
                '__import__': self._safe_import
            }
        }
        return globals_dict
    
    def _safe_import(self, name: str, globals=None, locals=None, fromlist=(), level=0) -> Any:
        """安全的模块导入
        
        Args:
            name: 模块名
            globals: 全局变量字典
            locals: 局部变量字典
            fromlist: 要导入的子模块列表
            level: 相对导入级别
            
        Returns:
            Any: 导入的模块
            
        Raises:
            SandboxError: 如果导入被禁止或模块不安全
        """
        if not self.settings.allow_imports:
            raise SandboxError("模块导入被禁止")
        
        if name in self.settings.allowed_modules:
            return __import__(name, globals, locals, fromlist, level)
        
        raise SandboxError(f"不允许导入模块: {name}")
    
    def is_path_allowed(self, path: str) -> bool:
        """检查路径是否允许访问
        
        Args:
            path: 要检查的路径
            
        Returns:
            bool: 是否允许访问
        """
        if not self.settings.allow_file_operations:
            return False
        
        try:
            abs_path = os.path.abspath(path)
            for allowed_dir in self.settings.allowed_directories:
                if abs_path.startswith(os.path.abspath(allowed_dir)):
                    return True
            return False
        except Exception:
            return False
    
    def allow_network_access(self) -> bool:
        """检查是否允许网络访问
        
        Returns:
            bool: 是否允许网络访问
        """
        return self.settings.network_access
    
    def allow_file_operations(self) -> bool:
        """检查是否允许文件操作
        
        Returns:
            bool: 是否允许文件操作
        """
        return self.settings.allow_file_operations
    
    def update_settings(self, settings: SandboxSettings) -> None:
        """更新沙箱设置
        
        Args:
            settings: 新的沙箱配置
        """
        self.settings = settings
    
    def check_resources(self) -> bool:
        """检查资源使用情况
        
        Returns:
            bool: 是否超出限制
        """
        if not self._process:
            return True
        
        try:
            # 检查内存使用
            memory_info = self._process.memory_info()
            if memory_info.rss / 1024 / 1024 > self.settings.max_memory_mb:
                return False
            
            # 检查 CPU 使用
            cpu_percent = self._process.cpu_percent()
            if cpu_percent > self.settings.max_cpu_percent:
                return False
            
            # 检查执行时间
            if time.time() - self._start_time > self.settings.max_execution_time:
                return False
            
            return True
        except Exception:
            return False
    
    @contextmanager
    def _resource_monitor(self):
        """资源监控上下文管理器"""
        print("Starting resource monitor context")  # 调试信息
        self._start_time = time.time()
        self._process = psutil.Process()
        self._stop_monitor.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_resources)
        self._monitor_thread.start()
        
        try:
            yield
        finally:
            print("Cleaning up resource monitor")  # 调试信息
            self._stop_monitor.set()
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join()
            self._process = None
            self._monitor_thread = None
            print("Resource monitor cleanup completed")  # 调试信息
    
    def _monitor_resources(self):
        """监控资源使用情况"""
        check_interval = 0.1  # 检查间隔（秒）
        last_check = time.time()
        print("Starting resource monitor")  # 调试信息
        
        while not self._stop_monitor.is_set():
            current_time = time.time()
            if current_time - last_check >= check_interval:
                if not self.check_resources():
                    self._stop_monitor.set()
                    raise ResourceLimitExceeded("资源使用超出限制")
                last_check = current_time
            time.sleep(0.01)  # 短暂休眠以减少 CPU 使用
        print("Resource monitor stopped")  # 调试信息
    
    def execute(self, code: str) -> Any:
        """执行代码
        
        Args:
            code: 要执行的代码
            
        Returns:
            Any: 执行结果
            
        Raises:
            SandboxError: 如果执行出错
            ResourceLimitExceeded: 如果资源使用超出限制
        """
        try:
            with self._resource_monitor():
                # 创建新的命名空间
                local_vars = {}
                
                # 执行代码
                exec(code, self._globals, local_vars)
                
                # 返回结果
                return local_vars.get('__result__')
        except ResourceLimitExceeded as e:
            raise
        except Exception as e:
            raise SandboxError(f"代码执行出错: {str(e)}")
    
    def cleanup(self) -> None:
        """清理资源"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_monitor.set()
            self._monitor_thread.join()
        self._process = None
        self._monitor_thread = None