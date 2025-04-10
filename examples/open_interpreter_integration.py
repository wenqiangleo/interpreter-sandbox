"""
Open Interpreter 集成示例
"""

from sandbox.integration.open_interpreter import OpenInterpreterSandbox
from sandbox.config.settings import SandboxSettings

def main():
    # 创建集成沙箱实例
    sandbox = OpenInterpreterSandbox()
    
    # 执行代码
    try:
        result = sandbox.execute_code_sync("""
x = 1 + 1
__result__ = x
""")
        print(f"执行结果: {result}")
    except Exception as e:
        print(f"执行出错: {e}")
    
    # 使用自定义配置
    settings = SandboxSettings(
        max_memory_mb=100,  # 限制内存使用为100MB
        max_cpu_percent=50,  # 限制CPU使用率为50%
        max_execution_time=5,  # 限制执行时间为5秒
        allowed_directories=["./"],  # 允许访问当前目录
        network_access=True,  # 禁止网络访问
        allow_file_operations=True,  # 禁止文件操作
        allow_imports=True,  # 允许导入模块
        allowed_modules=['math', 'random', 'json']  # 允许导入的模块
    )
    
    custom_sandbox = OpenInterpreterSandbox(settings)
    
    # 检查权限
    print(f"当前目录访问权限: {custom_sandbox.is_path_allowed('.')}")
    print(f"网络访问权限: {custom_sandbox.allow_network_access()}")
    print(f"文件操作权限: {custom_sandbox.allow_file_operations()}")
    
    # 测试受限操作
    try:
        result = custom_sandbox.execute_code_sync("""
import os
__result__ = os.listdir('.')
""")
    except Exception as e:
        print(f"执行受限操作出错: {e}")

if __name__ == "__main__":
    main() 