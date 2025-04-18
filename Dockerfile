FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ /app/src/
COPY examples/ /app/examples/
COPY tests/ /app/tests/

# 创建日志目录
RUN mkdir -p /app/logs

# 安装沙箱模块
RUN pip install -e .

# 暴露Web UI端口
EXPOSE 5000

# 设置环境变量
ENV PYTHONPATH=/app

# 启动Web UI服务
CMD ["python", "-m", "sandbox.web.app"]