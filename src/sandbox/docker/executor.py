"""
Docker容器内代码执行器
"""

import os
import json
import sys
import traceback
from sandbox.core.sandbox import Sandbox
from sandbox.config.settings import SandboxSettings

def run_code(execution_id: str) -> None:
    """在Docker容器内执行代码
    
    Args:
        execution_id: 执行ID，用于标识相关文件
    """
    # 设置文件路径
    temp_dir = "/app/temp"
    code_file = os.path.join(temp_dir, f"{execution_id}.py")
    settings_file = os.path.join(temp_dir, f"{execution_id}.json")
    result_file = os.path.join(temp_dir, f"{execution_id}_result.json")
    
    try:
        # 读取代码
        with open(code_file, 'r') as f:
            code = f.read()
        
        # 读取设置
        with open(settings_file, 'r') as f:
            settings_dict = json.load(f)
            settings = SandboxSettings(**settings_dict)
        
        # 创建沙箱并执行代码
        sandbox = Sandbox(settings, enable_logging=True)
        result = sandbox.execute(code)
        
        # 写入结果
        with open(result_file, 'w') as f:
            json.dump({"result": result}, f)
            
    except Exception as e:
        # 捕获异常并写入错误信息
        error_message = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        with open(result_file, 'w') as f:
            json.dump({"error": error_message}, f)
        
        # 打印错误信息
        print(error_message, file=sys.stderr)
        sys.exit(1)