import os
from dotenv import load_dotenv
import requests
from abc import ABC, abstractmethod

# 加载环境变量
load_dotenv()

class BaseAgent(ABC):
    """基础智能体类"""
    
    def __init__(self):
        """初始化基础智能体"""
        self.api_url = os.getenv("API_URL")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
        self.news_api_key = os.getenv("NEWS_API_KEY")
    
    def call_llm_api(self, prompt, temperature=0.7):
        """调用大语言模型API
        
        Args:
            prompt (str): 提示词
            temperature (float): 温度参数，控制随机性
            
        Returns:
            str: 模型回复内容
        """
        headers = {
            "Authorization": f"Bearer {self.refresh_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"调用LLM API失败: {e}")
            return "无法获取模型回复"
    
    @abstractmethod
    def collect_news(self):
        """收集新闻的抽象方法，需要被子类实现"""
        pass 