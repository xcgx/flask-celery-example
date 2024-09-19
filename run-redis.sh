#!/bin/bash

# 设置错误处理
set -e

# 检查并下载 Redis
if [ ! -d redis-stable ]; then
    echo "Downloading Redis..."
    curl -O http://download.redis.io/redis-stable.tar.gz
    tar xvzf redis-stable.tar.gz
    rm redis-stable.tar.gz
fi

# 进入 Redis 目录
cd redis-stable

# 编译 Redis
echo "Compiling Redis..."
make

# 检查编译是否成功
if [ ! -f src/redis-server ]; then
    echo "Error: Redis server binary not found!"
    exit 1
fi

# 启动 Redis 服务器
echo "Starting Redis server..."
src/redis-server &
REDIS_PID=$!

# 等待 Redis 服务器启动
sleep 2

# 检查 Redis 服务器是否启动成功
if ps -p $REDIS_PID > /dev/null; then
    echo "Redis server started successfully with PID $REDIS_PID"
else
    echo "Error: Failed to start Redis server!"
    exit 1
fi

# 保持脚本运行，防止 Redis 服务器进程被终止
wait $REDIS_PID

