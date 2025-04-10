"""
沙箱异常定义模块
"""

class SandboxError(Exception):
    """沙箱错误基类"""
    pass

class ResourceLimitExceeded(SandboxError):
    """资源限制超出错误"""
    pass

class SecurityError(SandboxError):
    """安全错误"""
    pass 