"""
Web UI 界面，用于展示代码执行的安全状态和资源使用情况
"""

from flask import Flask, render_template, request, jsonify
import threading
import time
import uuid
import os
import json
from sandbox.core.sandbox import Sandbox
from sandbox.config.settings import SandboxSettings
from sandbox.exceptions import SandboxError, ResourceLimitExceeded

# 初始化Flask应用
app = Flask(__name__)

# 存储执行历史
execution_history = []

# 存储实时资源使用数据
resource_data = {}

class ResourceMonitor(threading.Thread):
    """资源监控线程"""
    
    def __init__(self, execution_id, sandbox):
        threading.Thread.__init__(self)
        self.execution_id = execution_id
        self.sandbox = sandbox
        self.running = True
        self.data = []
    
    def run(self):
        start_time = time.time()
        while self.running and self.sandbox._process:
            try:
                # 获取资源使用情况
                memory_info = self.sandbox._process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                cpu_percent = self.sandbox._process.cpu_percent()
                elapsed_time = time.time() - start_time
                
                # 记录数据
                self.data.append({
                    'timestamp': time.time(),
                    'memory_mb': memory_mb,
                    'cpu_percent': cpu_percent,
                    'elapsed_time': elapsed_time
                })
                
                # 更新全局数据
                resource_data[self.execution_id] = self.data
                
                time.sleep(0.1)
            except:
                break
    
    def stop(self):
        self.running = False

@app.route('/')
def index():
    """返回首页"""
    return render_template('index.html', history=execution_history)

@app.route('/execute', methods=['POST'])
def execute_code():
    """执行代码并返回结果"""
    code = request.form.get('code', '')
    
    # 获取沙箱设置
    max_memory_mb = int(request.form.get('max_memory_mb', 100))
    max_cpu_percent = int(request.form.get('max_cpu_percent', 50))
    max_execution_time = int(request.form.get('max_execution_time', 5))
    allow_file_operations = request.form.get('allow_file_operations') == 'true'
    network_access = request.form.get('network_access') == 'true'
    allow_imports = request.form.get('allow_imports') == 'true'
    allowed_modules = request.form.get('allowed_modules', 'math,random,json').split(',')
    
    settings = SandboxSettings(
        max_memory_mb=max_memory_mb,
        max_cpu_percent=max_cpu_percent,
        max_execution_time=max_execution_time,
        allow_file_operations=allow_file_operations,
        network_access=network_access,
        allow_imports=allow_imports,
        allowed_modules=allowed_modules
    )
    
    sandbox = Sandbox(settings, enable_logging=True)
    
    execution_id = str(uuid.uuid4())
    start_time = time.time()
    
    # 启动资源监控线程
    monitor = ResourceMonitor(execution_id, sandbox)
    monitor.start()
    
    try:
        # 执行代码
        result = sandbox.execute(code)
        status = "成功"
        error = None
    except ResourceLimitExceeded as e:
        status = "资源超限"
        result = None
        error = str(e)
    except SandboxError as e:
        status = "沙箱错误"
        result = None
        error = str(e)
    except Exception as e:
        status = "执行失败"
        result = None
        error = str(e)
    finally:
        # 停止资源监控
        monitor.stop()
        
        # 计算执行时间
        execution_time = time.time() - start_time
        
        # 记录执行历史
        execution_record = {
            'id': execution_id,
            'timestamp': start_time,
            'code': code,
            'status': status,
            'result': result,
            'error': error,
            'execution_time': execution_time,
            'settings': settings.__dict__
        }
        execution_history.insert(0, execution_record)
        
        # 保留最近的50条记录
        if len(execution_history) > 50:
            old_id = execution_history.pop().get('id')
            if old_id in resource_data:
                del resource_data[old_id]
    
    return jsonify({
        'id': execution_id,
        'status': status,
        'result': result,
        'error': error,
        'execution_time': execution_time
    })

@app.route('/resource_data/<execution_id>')
def get_resource_data(execution_id):
    """获取资源使用数据"""
    if execution_id in resource_data:
        return jsonify(resource_data[execution_id])
    return jsonify([])

@app.route('/history/<execution_id>')
def get_execution_detail(execution_id):
    """获取执行详情"""
    for record in execution_history:
        if record['id'] == execution_id:
            return render_template('detail.html', record=record)
    return "执行记录不存在", 404

def run_server(host='0.0.0.0', port=5000, debug=False):
    """运行Web服务器"""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_server(debug=True)