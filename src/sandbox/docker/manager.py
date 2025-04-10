"""
Docker容器管理模块，用于在Docker容器中执行代码
"""

import docker
import os
import tempfile
import uuid
import json
from typing import Dict, Any, Optional
from sandbox.config.settings import SandboxSettings
from sandbox.exceptions import SandboxError

class DockerSandbox:
    """Docker沙箱容器管理类"""
    
    def __init__(self, settings: Optional[SandboxSettings] = None):
        """初始化Docker沙箱
        
        Args:
            settings: 沙箱配置，如果为None则使用默认配置
        """
        self.settings = settings or SandboxSettings()
        self.client = docker.from_env()
        self.image_name = "sandbox-interpreter:latest"
        self._ensure_image_exists()
    
    def _ensure_image_exists(self) -> None:
        """确保Docker镜像存在"""
        try:
            self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            raise SandboxError(f"Docker镜像 {self.image_name} 不存在，请先构建镜像")
    
    def execute(self, code: str) -> Any:
        """在Docker容器中执行代码
        
        Args:
            code: 要执行的代码
        
        Returns:
            执行结果
        """
        # 创建临时目录用于文件交换
        temp_dir = tempfile.mkdtemp()
        try:
            # 创建唯一的执行ID
            execution_id = str(uuid.uuid4())
            
            # 准备代码和设置文件
            code_file = os.path.join(temp_dir, f"{execution_id}.py")
            settings_file = os.path.join(temp_dir, f"{execution_id}.json")
            result_file = os.path.join(temp_dir, f"{execution_id}_result.json")
            
            # 写入代码文件
            with open(code_file, 'w') as f:
                f.write(code)
            
            # 写入设置文件
            with open(settings_file, 'w') as f:
                json.dump(self.settings.__dict__, f)
            
            # 运行Docker容器
            container = self.client.containers.run(
                image=self.image_name,
                command=f"python -c \"from sandbox.docker.executor import run_code; run_code('{execution_id}')\"",
                volumes={
                    temp_dir: {'bind': '/app/temp', 'mode': 'rw'}
                },
                mem_limit=f"{self.settings.max_memory_mb + 50}m",  # 添加额外的内存供容器本身使用
                cpu_period=100000,
                cpu_quota=int(100000 * self.settings.max_cpu_percent / 100),
                detach=True,
                network_mode="none" if not self.settings.network_access else "bridge",
                remove=True
            )
            
            # 等待容器执行完成
            result = container.wait(timeout=self.settings.max_execution_time + 5)
            
            # 检查执行状态
            if result['StatusCode'] != 0:
                # 获取容器日志
                logs = container.logs().decode('utf-8')
                raise SandboxError(f"Docker容器执行失败: {logs}")
            
            # 读取执行结果
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    result_data = json.load(f)
                    
                if 'error' in result_data:
                    raise SandboxError(result_data['error'])
                    
                return result_data.get('result')
            else:
                raise SandboxError("执行结果文件不存在")
                
        finally:
            # 清理临时文件
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def execute_async(self, code: str, callback=None):
        """异步执行代码
        
        Args:
            code: 要执行的代码
            callback: 执行完成后的回调函数
        """
        import threading
        
        def _execute_thread():
            try:
                result = self.execute(code)
                if callback:
                    callback(result=result, error=None)
            except Exception as e:
                if callback:
                    callback(result=None, error=str(e))
        
        thread = threading.Thread(target=_execute_thread)
        thread.daemon = True
        thread.start()
        return thread