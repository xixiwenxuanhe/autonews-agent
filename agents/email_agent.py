import os
import smtplib
import re
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from .base_agent import BaseAgent

class EmailAgent(BaseAgent):
    """邮件发送智能体"""
    
    def __init__(self):
        """初始化邮件发送智能体"""
        super().__init__()
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
        # 从环境变量中获取收件人邮箱列表
        email_receiver = os.getenv("EMAIL_RECEIVER", "")
        
        print(f"原始邮箱接收者设置: '{email_receiver}'")
        
        # 分离邮箱地址并确保去除空格和空字符串
        raw_emails = email_receiver.split(",")
        self.recipient_emails = []
        
        for email in raw_emails:
            cleaned_email = email.strip()
            if cleaned_email:  # 确保不是空字符串
                self.recipient_emails.append(cleaned_email)
                
        # 打印调试信息
        if self.recipient_emails:
            print(f"已配置的收件人邮箱: {self.recipient_emails}")
        else:
            print("警告: 未配置有效的收件人邮箱地址！")
        
        self.sent_count = 0
        
    def collect_news(self):
        """实现抽象方法，邮件发送智能体不需要收集新闻，返回空列表即可
        
        Returns:
            list: 空的新闻列表
        """
        return []
    
    def send_email(self, html_content):
        """发送邮件给多个收件人
        
        Args:
            html_content (str): 邮件HTML内容
            
        Returns:
            bool: 是否发送成功
        """
        if not self.recipient_emails:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 未指定有效的收件人邮箱，发送失败")
            print(f"请检查.env文件中的EMAIL_RECEIVER配置，确保正确设置并且不为空")
            return False
            
        # 检查其他必需配置是否存在
        if not self.smtp_server:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 未指定SMTP服务器，发送失败")
            print("请在.env文件中设置SMTP_SERVER变量")
            return False
            
        if not self.sender_email:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 未指定发件人邮箱，发送失败")
            print("请在.env文件中设置SENDER_EMAIL变量")
            return False
            
        if not self.email_password:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 未指定邮箱密码，发送失败")
            print("请在.env文件中设置EMAIL_PASSWORD变量")
            return False
            
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 待发送邮件的收件人列表: {self.recipient_emails} (共{len(self.recipient_emails)}个)")
            
        today = datetime.now().strftime("%Y年%m月%d日")
        subject = f"每日新闻摘要 (科技/经济) - {today}"
        
        success_count = 0
        failed_count = 0
            
        # 为每个收件人单独发送邮件
        for i, recipient_email in enumerate(self.recipient_emails):
            try:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 正在处理第 {i+1}/{len(self.recipient_emails)} 个收件人: {recipient_email}")
                
                # 为每个收件人创建新的SMTP连接
                smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, 'utf-8')
                
                # 登录
                smtp.login(self.sender_email, self.email_password)
                
                # 创建邮件对象
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.sender_email
                msg['To'] = recipient_email
                
                # 添加HTML内容
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
                
                # 发送邮件
                smtp.sendmail(self.sender_email, recipient_email, msg.as_string())
                
                # 关闭SMTP连接
                smtp.quit()
                
                success_count += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 邮件已成功发送至 {recipient_email}")
                
            except Exception as e:
                failed_count += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 发送邮件到 {recipient_email} 失败: {str(e)}")
            
            # 如果还有下一个收件人，等待1秒钟
            if i < len(self.recipient_emails) - 1:
                time.sleep(1)
            
        # 更新发送计数
        self.sent_count += success_count
        
        # 打印发送统计
        if success_count > 0 and failed_count == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 所有邮件发送成功 ({success_count}/{len(self.recipient_emails)})")
            return True
        elif success_count > 0 and failed_count > 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ 部分邮件发送成功 ({success_count}/{len(self.recipient_emails)})")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 所有邮件发送失败")
            return False
    
    def get_stats(self):
        """获取邮件发送统计数据
        
        Returns:
            dict: 统计数据
        """
        stats = {
            "sent_count": self.sent_count,
            "recipient_count": len(self.recipient_emails),
            "last_sent": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return stats 