#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import threading
import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from pathlib import Path
from dotenv import load_dotenv
import io
from datetime import datetime
from contextlib import redirect_stdout

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入项目模块
from agents.email_agent import EmailAgent
from agents.search_agent import SearchAgent
from agents.integration_agent import ContentIntegrationAgent

# 初始化Flask应用
app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局任务状态
current_task = None
task_output = []

# 自定义输出捕获类，用于将print输出重定向到WebSocket
class OutputCapture(io.StringIO):
    def write(self, text):
        super().write(text)
        if text.strip():  # 只发送非空内容
            socketio.emit('output', {'data': text})
            socketio.sleep(0)  # 确保WebSocket立即发送数据

# 路由：主页
@app.route('/')
def index():
    load_dotenv()  # 加载环境变量
    return render_template('index.html')

# 路由：开始任务
@app.route('/api/run', methods=['POST'])
def run_task():
    global current_task, task_output
    
    # 获取参数
    data = request.json
    hard = data.get('hard', False)
    send = data.get('send', False)
    emails = data.get('emails', [])
    
    # 如果邮箱列表非空，覆盖环境变量
    if emails:
        os.environ['EMAIL_RECEIVER'] = ', '.join(emails)
    
    # 如果有任务正在运行，返回错误
    if current_task and current_task.is_alive():
        return jsonify({'success': False, 'message': '已有任务正在运行，请等待完成'})
    
    # 清空上一个任务的输出
    task_output = []
    
    # 创建并启动新任务
    current_task = threading.Thread(target=run_news_aggregation_task, args=(hard, send))
    current_task.start()
    
    return jsonify({'success': True, 'message': '任务已启动'})

# 路由：获取任务状态
@app.route('/api/status', methods=['GET'])
def get_status():
    global current_task
    
    if current_task and current_task.is_alive():
        return jsonify({'status': 'running'})
    elif current_task:
        return jsonify({'status': 'completed'})
    else:
        return jsonify({'status': 'idle'})

# 任务主函数（在单独的线程中运行）
def run_news_aggregation_task(hard=False, send=True):
    """运行新闻聚合流程"""
    # 捕获标准输出并重定向到WebSocket
    with redirect_stdout(OutputCapture()) as captured:
        start_time = datetime.now()
        print(f"\n[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] 🚀 开始新闻聚合流程")
        
        try:
            # 初始化各个智能体
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 开始处理: 初始化智能体")
            search_agent = SearchAgent()
            integration_agent = ContentIntegrationAgent()
            email_agent = EmailAgent()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 处理完成: 初始化智能体")
            
            # 收集各类新闻
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 开始处理: 收集所有领域新闻")
            all_news = search_agent.collect_news(hard=hard)
            tech_news = all_news.get("technology", [])
            economy_news = all_news.get("economy", [])
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 处理完成: IT科技新闻 (获取到 {len(tech_news)} 条)")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 处理完成: 经济新闻 (获取到 {len(economy_news)} 条)")
            
            # 整合内容
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 开始处理: 整合新闻内容")
            email_content = integration_agent.integrate_content(
                tech_news=tech_news,
                economy_news=economy_news
            )
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 处理完成: 整合新闻内容")
            
            # 只有在send为True时才发送邮件
            if send:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 开始处理: 发送邮件")
                email_agent.send_email(email_content)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 处理完成: 发送邮件")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️ 邮件发送已禁用 (send=False)，跳过发送步骤")
            
            # 计算总耗时
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 新闻聚合流程完成 - 总耗时: {duration:.2f} 秒")
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 处理过程中出错: {str(e)}")
            logger.exception("任务执行出错")

# 启动应用
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True) 