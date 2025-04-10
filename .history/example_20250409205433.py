from src.sandbox.core.sandbox import Sandbox
from src.sandbox.config.sandbox_config import SandboxConfig, ResourceLimits, FileSystemAccess, NetworkAccess
import os

def main():
    # 获取当前工作目录
    current_dir = os.getcwd()
    data_dir = os.path.join(current_dir, "data")

    # 创建沙箱配置
    config = SandboxConfig(
        resource_limits=ResourceLimits(
            cpu_time_limit=30,  # 30秒CPU时间限制
            memory_limit=256 * 1024 * 1024,  # 256MB内存限制
            max_processes=5,
            max_files=100
        ),
        file_system=FileSystemAccess(
            allowed_paths=[data_dir],  # 只允许访问data目录
            read_only=True
        ),
        network=NetworkAccess(
            allow_network=False  # 禁止网络访问
        ),
        allowed_modules=["math", "json"]  # 只允许导入math和json模块
    )

    # 示例1：执行简单的数学计算
    print("示例1：执行简单的数学计算")
    with Sandbox(config) as sandbox:
        result = sandbox.execute("1 + 2 * 3")
        print(f"计算结果: {result}")

    # 示例2：使用允许的模块
    print("\n示例2：使用允许的模块")
    with Sandbox(config) as sandbox:
        code = """
import math
result = math.sqrt(16)
print(f"平方根计算结果: {result}")
"""
        result = sandbox.execute(code)

    # 示例3：尝试访问被禁止的模块（会抛出SecurityError）
    print("\n示例3：尝试访问被禁止的模块")
    try:
        with Sandbox(config) as sandbox:
            code = """
import os
print(os.listdir('.'))
"""
            sandbox.execute(code)
    except Exception as e:
        print(f"预期中的错误: {str(e)}")

    # 示例4：尝试网络访问（会抛出SecurityError）
    print("\n示例4：尝试网络访问")
    try:
        with Sandbox(config) as sandbox:
            code = """
import urllib.request
urllib.request.urlopen('http://example.com')
"""
            sandbox.execute(code)
    except Exception as e:
        print(f"预期中的错误: {str(e)}")

    # 示例5：尝试访问允许的文件
    print("\n示例5：尝试访问允许的文件")
    try:
        with Sandbox(config) as sandbox:
            code = f"""
with open(r'{os.path.join(data_dir, "test.txt")}', 'r') as f:
    content = f.read()
    print(f"文件内容: {{content}}")
"""
            sandbox.execute(code)
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    main() 