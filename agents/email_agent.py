import os
import smtplib
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
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        self.sent_count = 0
    
    def collect_news(self):
        """实现抽象方法，邮件发送智能体不需要收集新闻，返回空列表即可
        
        Returns:
            list: 空的新闻列表
        """
        return []
    
    def send_email(self, html_content):
        """发送邮件
        
        Args:
            html_content (str): 邮件HTML内容
            
        Returns:
            bool: 是否发送成功
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📧 发送邮件...")
        
        today = datetime.now().strftime("%Y年%m月%d日")
        subject = f"每日新闻摘要 - {today}"
        
        # 创建邮件对象
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        
        # 添加HTML内容
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        try:
            # 连接到SMTP服务器并发送邮件
            smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, 'utf-8')
            smtp.login(self.sender_email, self.email_password)
            smtp.sendmail(self.sender_email, self.recipient_email, msg.as_string())
            smtp.quit()
            
            # 更新发送计数
            self.sent_count += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 邮件已发送至 {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 发送邮件失败: {e}")
            return False
    
    def get_stats(self):
        """获取邮件发送统计数据
        
        Returns:
            dict: 统计数据
        """
        stats = {
            "sent_count": self.sent_count,
            "last_sent": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return stats 