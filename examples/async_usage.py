"""
沙箱环境异步使用示例
"""

import asyncio
from sandbox import Sandbox, SandboxSettings

async def main():
    # 创建沙箱实例
    sandbox = Sandbox()
    
    # 异步执行代码
    result = await sandbox.execute_async("""
x = 1 + 1
__result__ = x
""")
    print(f"异步执行结果: {result}")
    
    # 并发执行多个任务
    tasks = [
        sandbox.execute_async(f"""
import time
time.sleep(1)
__result__ = {i}
""")
        for i in range(5)
    ]
    
    results = await asyncio.gather(*tasks)
    print(f"并发执行结果: {results}")
    
    # 使用自定义配置
    settings = SandboxSettings(
        max_memory_mb=100,
        max_cpu_percent=50,
        max_execution_time=2
    )
    
    custom_sandbox = Sandbox(settings)
    
    # 测试超时
    try:
        await custom_sandbox.execute_async("""
import time
time.sleep(3)  # 超过2秒限制
__result__ = True
""")
    except Exception as e:
        print(f"执行超时: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 