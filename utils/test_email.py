#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
邮件发送功能测试脚本
用于直接测试邮件发送功能，不经过新闻收集和整合流程
"""

import os
import sys
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# 将项目根目录添加到模块搜索路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.email_agent import EmailAgent

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="邮件发送测试")
    parser.add_argument("--email", type=str, help="指定测试用邮箱，不提供则使用.env中的所有邮箱")
    parser.add_argument("--delay", type=int, default=1, help="邮件发送间隔(秒)，默认1秒")
    args = parser.parse_args()
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    
    # 加载环境变量
    print(f"从 {env_path} 加载环境变量...")
    load_dotenv(dotenv_path=env_path, override=True)
    
    # 初始化邮件代理
    email_agent = EmailAgent()
    
    # 准备收件人列表
    all_recipients = email_agent.recipient_emails.copy()
    
    # 如果指定了特定邮箱进行测试
    if args.email:
        print(f"使用指定的测试邮箱: {args.email}")
        test_recipients = [args.email.strip()]
    else:
        test_recipients = all_recipients
        print(f"使用所有配置的邮箱: {test_recipients}")
    
    if not test_recipients:
        print("❌ 没有有效的收件人邮箱，请检查配置或使用--email参数指定")
        return
    
    # 生成简单的测试内容
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>测试邮件</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }}
            h1 {{ color: #2c3e50; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>执行测试</h1>
            <p>这是一封简单的测试邮件，用于验证邮件发送功能。</p>
            <p>发送时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </body>
    </html>
    """
    
    # 单独为每个收件人发送邮件
    success_count = 0
    
    for i, recipient in enumerate(test_recipients):
        print(f"\n===== 正在处理第 {i+1}/{len(test_recipients)} 个收件人: {recipient} =====")
        
        # 临时替换EmailAgent的收件人列表，只包含当前收件人
        email_agent.recipient_emails = [recipient]
        
        # 发送测试邮件
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始发送邮件...")
        success = email_agent.send_email(html_content)
        
        if success:
            success_count += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 邮件发送成功")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 邮件发送失败")
        
        # 如果还有下一个收件人，等待指定时间
        if i < len(test_recipients) - 1:
            wait_time = args.delay
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🕒 等待 {wait_time} 秒后处理下一个收件人...")
            time.sleep(wait_time)
    
    # 恢复EmailAgent的原始收件人列表
    email_agent.recipient_emails = all_recipients
    
    # 输出总结
    print(f"\n===== 测试完成 =====")
    print(f"总发送: {len(test_recipients)} 封邮件")
    print(f"成功: {success_count} 封")
    print(f"失败: {len(test_recipients) - success_count} 封")
    
    if success_count == len(test_recipients):
        print("\n✅ 所有邮件发送成功！")
    elif success_count > 0:
        print("\n⚠️ 部分邮件发送成功，部分失败")
    else:
        print("\n❌ 所有邮件发送失败！")

if __name__ == "__main__":
    main() 