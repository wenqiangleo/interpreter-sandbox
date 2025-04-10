from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import psutil
import time
import asyncio
from ..sandbox.sandbox import Sandbox, SandboxError

app = FastAPI(
    title="Open Interpreter Sandbox",
    description="安全的代码执行沙箱环境",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str
    timeout: Optional[int] = 30
    memory_limit: Optional[int] = 512 * 1024 * 1024
    cpu_limit: Optional[float] = 1.0
    network_enabled: Optional[bool] = False
    allowed_modules: Optional[list] = None

class ExecutionResult(BaseModel):
    success: bool
    output: Optional[str]
    error: Optional[str]
    execution_time: float
    memory_used: int
    cpu_used: float
    system_status: Dict[str, Any]

@app.post("/execute", response_model=ExecutionResult)
async def execute_code(request: CodeRequest):
    """执行代码并返回结果"""
    try:
        sandbox = Sandbox(
            timeout=request.timeout,
            memory_limit=request.memory_limit,
            cpu_limit=request.cpu_limit,
            network_enabled=request.network_enabled,
            allowed_modules=request.allowed_modules
        )
        
        # 异步执行代码
        result = await sandbox.execute_async(request.code)
        
        # 获取系统状态
        system_status = await get_system_status()
        
        return ExecutionResult(
            success=result['success'],
            output=result.get('output'),
            error=result.get('error'),
            execution_time=result['execution_time'],
            memory_used=result['memory_used'],
            cpu_used=result['cpu_used'],
            system_status=system_status
        )
        
    except SandboxError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

async def get_system_status() -> Dict[str, Any]:
    """获取系统状态"""
    loop = asyncio.get_event_loop()
    
    # 异步获取系统状态
    cpu_percent = await loop.run_in_executor(None, psutil.cpu_percent)
    memory = await loop.run_in_executor(None, psutil.virtual_memory)
    disk = await loop.run_in_executor(None, psutil.disk_usage, '/')
    
    return {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_available": memory.available,
        "disk_usage": disk.percent,
        "disk_free": disk.free
    }

@app.get("/status")
async def get_status():
    """获取系统状态"""
    try:
        return await get_system_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统状态失败: {str(e)}") 