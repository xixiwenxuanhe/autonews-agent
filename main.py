import os
import time
import schedule
from dotenv import load_dotenv
from datetime import datetime

from agents.tech_agent import TechNewsAgent
from agents.economy_agent import EconomyNewsAgent
from agents.science_agent import ScienceNewsAgent
from agents.integration_agent import ContentIntegrationAgent
from agents.email_agent import EmailAgent

# 加载环境变量
load_dotenv()

def run_news_aggregation():
    """运行新闻聚合流程"""
    print(f"开始运行新闻聚合流程 - {datetime.now()}")
    
    # 初始化各个智能体
    tech_agent = TechNewsAgent()
    economy_agent = EconomyNewsAgent()
    science_agent = ScienceNewsAgent()
    integration_agent = ContentIntegrationAgent()
    email_agent = EmailAgent()
    
    # 收集各类新闻
    tech_news = tech_agent.collect_news()
    economy_news = economy_agent.collect_news()
    science_news = science_agent.collect_news()
    
    # 整合内容
    email_content = integration_agent.integrate_content(
        tech_news=tech_news,
        economy_news=economy_news,
        science_news=science_news
    )
    
    # 发送邮件
    email_agent.send_email(email_content)
    
    print(f"新闻聚合流程完成 - {datetime.now()}")

def main():
    # 获取定时配置
    schedule_time = os.getenv("SCHEDULE_TIME", "07:00")
    
    # 设置定时任务
    schedule.every().day.at(schedule_time).do(run_news_aggregation)
    
    print(f"新闻聚合系统已启动，将在每天 {schedule_time} 运行")
    
    # 立即运行一次
    run_news_aggregation()
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 