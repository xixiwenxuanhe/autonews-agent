import os
import time
import schedule
import argparse
from dotenv import load_dotenv
from datetime import datetime

from agents.search_agent import SearchAgent
from agents.integration_agent import ContentIntegrationAgent
from agents.email_agent import EmailAgent

# 加载环境变量
load_dotenv()

# 调试信息格式化函数
def print_debug_info(message, is_start=True, is_result=False, result=None):
    """打印格式化的调试信息
    
    Args:
        message (str): 调试信息内容
        is_start (bool): 是否是开始处理的信息
        is_result (bool): 是否是结果信息
        result (any): 如果是结果信息，包含的结果数据
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if is_start:
        print(f"\n[{current_time}] 🚀 开始处理: {message}")
    elif is_result:
        print(f"[{current_time}] ✅ 处理完成: {message}")
        if result is not None:
            if isinstance(result, list):
                print(f"  📊 获取到 {len(result)} 条结果")
                # 显示中英文新闻数量
                zh_news = [news for news in result if news.get('language') == '中文']
                en_news = [news for news in result if news.get('language') == '英文']
                print(f"  🇨🇳 中文新闻: {len(zh_news)} 条")
                print(f"  🌍 英文新闻: {len(en_news)} 条")
            else:
                print(f"  📊 结果类型: {type(result)}")
    else:
        print(f"[{current_time}] ℹ️ {message}")

def run_news_aggregation(hard=False, sent=True):
    """运行新闻聚合流程
    
    Args:
        hard (bool): 是否使用硬编码的关键词对并打印搜索结果
        sent (bool): 是否发送邮件
    """
    start_time = datetime.now()
    print_debug_info(f"新闻聚合流程 - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化各个智能体
    print_debug_info("初始化智能体", is_start=True)
    search_agent = SearchAgent()
    integration_agent = ContentIntegrationAgent()
    email_agent = EmailAgent()
    print_debug_info("初始化智能体", is_start=False, is_result=True)
    
    # 收集各类新闻
    print_debug_info("收集所有领域新闻", is_start=True)
    all_news = search_agent.collect_news(hard=hard)
    tech_news = all_news.get("technology", [])
    science_news = all_news.get("science", [])
    economy_news = all_news.get("economy", [])
    print_debug_info("IT科技新闻", is_start=False, is_result=True, result=tech_news)
    print_debug_info("科学新闻", is_start=False, is_result=True, result=science_news)
    print_debug_info("经济新闻", is_start=False, is_result=True, result=economy_news)
    
    # 整合内容
    print_debug_info("整合新闻内容", is_start=True)
    email_content = integration_agent.integrate_content(
        tech_news=tech_news,
        economy_news=economy_news,
        science_news=science_news
    )
    print_debug_info("整合新闻内容", is_start=False, is_result=True)
    
    # 只有在sent为True时才发送邮件
    if sent:
        print_debug_info("发送邮件", is_start=True)
        email_agent.send_email(email_content)
        print_debug_info("发送邮件", is_start=False, is_result=True)
    else:
        print_debug_info("邮件发送已禁用 (sent=False)，跳过发送步骤", is_start=False)
    
    # 计算总耗时
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print_debug_info(f"新闻聚合流程完成 - 总耗时: {duration:.2f} 秒", is_result=True)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="新闻聚合系统")
    parser.add_argument("--hard", type=str, default="false", help="是否使用硬编码的关键词对并打印搜索结果")
    parser.add_argument("--sent", type=str, default="true", help="是否发送邮件")
    args = parser.parse_args()
    
    # 转换参数为布尔值
    use_hard = args.hard.lower() == "true"
    do_send = args.sent.lower() == "true"
    
    # 获取定时配置
    schedule_time = os.getenv("SCHEDULE_TIME", "07:00")
    
    # 设置定时任务
    schedule.every().day.at(schedule_time).do(run_news_aggregation, hard=use_hard, sent=do_send)
    
    print(f"新闻聚合系统已启动，将在每天 {schedule_time} 运行")
    print(f"参数设置: 硬编码关键词={use_hard}, 发送邮件={do_send}")
    
    # 立即运行一次
    run_news_aggregation(hard=use_hard, sent=do_send)
    
    # 持续运行定时任务
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 