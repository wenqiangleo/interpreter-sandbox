"""
安全日志记录模块，用于详细记录代码执行过程
"""

import logging
import os
import time
import json
from typing import Dict, Any, Optional

class SecurityLogger:
    """安全日志记录类"""
    
    def __init__(self, log_dir: str = "./logs", level: int = logging.INFO):
        """初始化安全日志记录器
        
        Args:
            log_dir: 日志文件目录
            level: 日志记录级别
        """
        self.log_dir = log_dir
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 设置文件日志
        self.logger = logging.getLogger("sandbox_security")
        self.logger.setLevel(level)
        
        # 创建日志文件处理器
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(log_dir, f"security-{timestamp}.log")
        file_handler = logging.FileHandler(log_file)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        self.logger.addHandler(file_handler)
        
        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        self.execution_id = None
        self.start_time = None
    
    def start_execution(self, execution_id: str, code: str, settings: Dict[str, Any]) -> None:
        """记录代码执行开始
        
        Args:
            execution_id: 执行ID
            code: 要执行的代码
            settings: 沙箱设置
        """
        self.execution_id = execution_id
        self.start_time = time.time()
        
        self.logger.info(f"开始执行代码 [ID: {execution_id}]")
        self.logger.info(f"代码内容:\n{code}")
        self.logger.info(f"沙箱设置: {json.dumps(settings, indent=2)}")
    
    def log_resource_usage(self, memory_mb: float, cpu_percent: float) -> None:
        """记录资源使用情况
        
        Args:
            memory_mb: 内存使用量(MB)
            cpu_percent: CPU使用率(%)
        """
        if self.execution_id:
            self.logger.info(f"资源使用 [ID: {self.execution_id}] - 内存: {memory_mb:.2f}MB, CPU: {cpu_percent:.2f}%")
    
    def log_file_access(self, path: str, operation: str, allowed: bool) -> None:
        """记录文件访问操作
        
        Args:
            path: 文件路径
            operation: 操作类型（读/写/执行）
            allowed: 是否允许访问
        """
        status = "允许" if allowed else "拒绝"
        self.logger.warning(f"文件访问 [ID: {self.execution_id}] - {status} {operation} 文件 {path}")
    
    def log_network_access(self, target: str, allowed: bool) -> None:
        """记录网络访问操作
        
        Args:
            target: 目标地址
            allowed: 是否允许访问
        """
        status = "允许" if allowed else "拒绝"
        self.logger.warning(f"网络访问 [ID: {self.execution_id}] - {status} 访问 {target}")
    
    def log_module_import(self, module: str, allowed: bool) -> None:
        """记录模块导入操作
        
        Args:
            module: 模块名称
            allowed: 是否允许导入
        """
        status = "允许" if allowed else "拒绝"
        self.logger.info(f"模块导入 [ID: {self.execution_id}] - {status} 导入 {module}")
    
    def log_error(self, error_type: str, message: str) -> None:
        """记录错误信息
        
        Args:
            error_type: 错误类型
            message: 错误消息
        """
        self.logger.error(f"执行错误 [ID: {self.execution_id}] - {error_type}: {message}")
    
    def end_execution(self, status: str, result: Optional[Any] = None) -> None:
        """记录代码执行结束
        
        Args:
            status: 执行状态（成功/失败）
            result: 执行结果
        """
        if self.start_time:
            execution_time = time.time() - self.start_time
            self.logger.info(f"执行结束 [ID: {self.execution_id}] - 状态: {status}, 耗时: {execution_time:.4f}秒")
            
            if result:
                self.logger.info(f"执行结果 [ID: {self.execution_id}]:\n{result}")
            
            self.execution_id = None
            self.start_time = None