from sandbox.integration.interpreter import InterpreterSandbox
from sandbox.config.settings import SandboxSettings

# 创建自定义设置
settings = SandboxSettings(
    max_memory_mb=200,            # 设置内存限制为200MB
    max_cpu_percent=30,           # 限制CPU使用率为30%
    max_execution_time=10,        # 执行超时时间10秒
    allowed_directories=["./data"],  # 只允许访问data目录
    network_access=False,         # 禁止网络访问
    allow_file_operations=True,   # 允许文件操作
    allow_imports=True,           # 允许导入模块
    allowed_modules=['math', 'pandas', 'matplotlib']  # 允许导入的模块列表
)

# 创建带有自定义设置的沙箱
sandbox = InterpreterSandbox(settings)

# 使用沙箱
result = sandbox.chat("请帮我分析./data/sample.csv文件")