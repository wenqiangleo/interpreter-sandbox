"""
Open Interpreter 集成使用示例
"""

import os
from sandbox.integration.interpreter import InterpreterSandbox
from sandbox.config.settings import SandboxSettings

def main():
    # 设置环境变量
    os.environ['INTERPRETER_API_BASE'] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    os.environ['INTERPRETER_MODEL'] = "qwq-plus"
    os.environ['INTERPRETER_API_KEY'] = "sk-bc4339fe8e8e48f6b57fab86b5d70afa"
    
    # 创建沙箱实例
    sandbox = InterpreterSandbox()
    
    try:
        # 基本使用
        print("开始基本使用测试...")
        result = sandbox.chat("你好，请帮我计算 1+1 的结果。")
        print(f"基本使用结果: {result}")
        
        # 使用自定义配置
        settings = SandboxSettings(
            max_memory_mb=100,      # 限制内存使用为100MB
            max_cpu_percent=50,     # 限制CPU使用率为50%
            max_execution_time=10,  # 限制执行时间为10秒
            allowed_directories=["./"],  # 允许访问当前目录
            network_access=True,    # 允许网络访问
            allow_file_operations=True,  # 允许文件操作
            allow_imports=True,     # 允许导入模块
            allowed_modules=['math', 'random', 'json', 'os']  # 允许导入的模块
        )
        
        # 更新配置
        sandbox.update_settings(settings)
        
        # 执行受限代码
        print("\n开始数学计算测试...")
        result = sandbox.chat("请计算16的平方根。")
        print(f"数学计算结果: {result}")
        
        # 检查权限
        print(f"\n当前目录访问权限: {sandbox.is_path_allowed('.')}")
        print(f"网络访问权限: {sandbox.allow_network_access()}")
        print(f"文件操作权限: {sandbox.allow_file_operations()}")
        
        # 尝试列出文件
        print("\n开始文件列表测试...")
        result = sandbox.chat("请列出当前目录下的文件。")
        print(f"文件列表结果: {result}")
        
    finally:
        # 清理资源
        print("\n清理资源...")
        sandbox.cleanup()
        print("测试完成。")

if __name__ == "__main__":
    main()