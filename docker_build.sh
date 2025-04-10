#!/bin/bash

# 构建Docker镜像
docker build -t sandbox-interpreter .

# 运行Docker容器
docker run -p 5000:5000 -v $(pwd)/logs:/app/logs --name sandbox-interpreter-container sandbox-interpreter