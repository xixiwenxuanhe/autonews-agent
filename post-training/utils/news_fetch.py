#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import requests
from datetime import datetime, timedelta
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('news_fetcher')

# 添加项目根目录到sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

# 加载.env文件
load_dotenv(project_root / '.env')

# 获取API密钥
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
if not NEWS_API_KEY:
    logger.error('NEWS_API_KEY未在.env文件中设置')
    sys.exit(1)

class NewsFetcher:
    def __init__(self, api_key=None):
        self.api_key = api_key or NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
        self.output_dir = project_root / 'post-training' / 'dataset'
        self.keywords_path = project_root / 'agents' / 'keywords.json'
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 存储所有标题的列表
        self.all_titles = []
    
    def load_keywords(self):
        """从keywords.json加载关键词"""
        try:
            with open(self.keywords_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载关键词文件时出错: {e}")
            return {}
    
    def fetch_news(self, keyword_pair, language='en', max_results=10):
        """使用关键词获取新闻"""
        # 将关键词数组转换为查询字符串 (keyword1 OR keyword2)
        query = f'({" OR ".join(keyword_pair)})'
        
        # 计算一周前的日期
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'language': language,
            'from': week_ago,
            'sortBy': 'relevancy',
            'pageSize': max_results,
            'apiKey': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json().get('articles', [])
        except requests.RequestException as e:
            logger.error(f"获取新闻API请求失败: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"API错误响应: {e.response.text}")
            return []
    
    def collect_titles(self, articles):
        """从文章中提取标题"""
        if not articles:
            return
        
        # 只提取标题并添加到列表中
        titles = [article.get('title', '') for article in articles if article.get('title')]
        self.all_titles.extend(titles)
        
        logger.info(f"已收集 {len(titles)} 个新闻标题")
    
    def save_all_titles(self):
        """将所有收集到的新闻标题保存到一个纯文本文件中"""
        if not self.all_titles:
            logger.warning("没有收集到任何新闻标题")
            return
        
        # 创建文件名
        filename = f"news_titles_{datetime.now().strftime('%Y%m%d')}.txt"
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 每行写入一个标题
                for title in self.all_titles:
                    f.write(f"{title}\n")
            
            logger.info(f"已将所有收集到的新闻标题（共 {len(self.all_titles)} 个）保存到 {file_path}")
        except Exception as e:
            logger.error(f"保存新闻标题时出错: {e}")
    
    def process_all_keywords(self):
        """处理所有关键词并获取新闻"""
        keywords_data = self.load_keywords()
        total_requests = 0
        
        for category, lang_keywords in keywords_data.items():
            logger.info(f"正在处理类别: {category}")
            
            for language, keyword_pairs in lang_keywords.items():
                logger.info(f"语言: {language}")
                
                for keyword_pair in keyword_pairs:
                    logger.info(f"获取关键词: {' OR '.join(keyword_pair)} 的新闻")
                    
                    # 获取新闻
                    articles = self.fetch_news(keyword_pair, language)
                    
                    # 收集标题
                    self.collect_titles(articles)
                    
                    total_requests += 1
                    
                    # NewsAPI免费账户限制: 100请求/天，添加延迟避免超出限制
                    time.sleep(1)  # 每次请求后暂停1秒
        
        # 将所有收集到的标题保存到一个文件中
        self.save_all_titles()
        
        logger.info(f"完成所有新闻获取，共发送 {total_requests} 个请求")

def main():
    logger.info("开始获取新闻数据...")
    fetcher = NewsFetcher()
    fetcher.process_all_keywords()
    logger.info("新闻数据获取完成")

if __name__ == "__main__":
    main()
