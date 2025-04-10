"""
沙箱环境基本使用示例
"""

from sandbox import Sandbox, SandboxSettings

def main():
    # 创建默认配置的沙箱
    sandbox = Sandbox()
    
    # 执行简单代码
    result = sandbox.execute("""
x = 1 + 1
__result__ = x
""")
    print(f"简单计算: {result}")
    
    # 使用自定义配置
    settings = SandboxSettings(
        max_memory_mb=100,  # 限制内存使用为100MB
        max_cpu_percent=50,  # 限制CPU使用率为50%
        max_execution_time=5,  # 限制执行时间为5秒
        allowed_directories=["./"],  # 允许访问当前目录
        network_access=True,  # 禁止网络访问
        allow_file_operations=True,  # 禁止文件操作
        allow_imports=True,  # 允许导入模块
        allowed_modules=['math', 'random', 'json','os']  # 允许导入的模块
    )
    
    custom_sandbox = Sandbox(settings)
    
    # 执行受限代码
    try:
        result = custom_sandbox.execute("""
import os
__result__ = os.listdir('.')
""")
    except Exception as e:
        print(f"执行受限代码出错: {e}")
        
    # 检查路径访问权限
    print(f"当前目录访问权限: {custom_sandbox.is_path_allowed('.')}")
    print(f"根目录访问权限: {custom_sandbox.is_path_allowed('/')}")
    
    # 检查网络访问权限
    print(f"网络访问权限: {custom_sandbox.allow_network_access()}")
    
    # 检查文件操作权限
    print(f"文件操作权限: {custom_sandbox.allow_file_operations()}")

if __name__ == "__main__":
    main() 