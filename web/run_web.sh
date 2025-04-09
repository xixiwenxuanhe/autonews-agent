#!/bin/bash

# 确保在正确的目录
cd "$(dirname "$0")"

# 显示启动信息
echo "正在启动新闻聚合系统Web界面..."
echo "可以通过浏览器访问: http://localhost:5000"

# 启动Web应用
python app.py

echo "Web服务已关闭" 