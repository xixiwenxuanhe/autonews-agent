import os
from dotenv import load_dotenv
import requests
from abc import ABC, abstractmethod
import re

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
    
    def is_traditional_chinese(self, text):
        """检测文本是否包含繁体中文
        
        Args:
            text (str): 需要检测的文本
            
        Returns:
            bool: 是否包含繁体中文
        """
        # 常见的简体-繁体对应字符
        trad_chars = {
            '髮': '发', '壹': '一', '貳': '二', '參': '三', '肆': '四',
            '為': '为', '這': '这', '說': '说', '對': '对', '時': '时',
            '從': '从', '會': '会', '來': '来', '學': '学', '國': '国',
            '與': '与', '產': '产', '內': '内', '係': '系', '點': '点',
            '實': '实', '發': '发', '經': '经', '關': '关', '樣': '样',
            '單': '单', '歲': '岁', '們': '们', '區': '区', '衝': '冲',
            '東': '东', '車': '车', '話': '话', '過': '过', '億': '亿',
            '預': '预', '當': '当', '體': '体', '麼': '么', '電': '电',
            '務': '务', '開': '开', '買': '买', '總': '总', '問': '问',
            '門': '门', '見': '见', '認': '认', '隻': '只', '飛': '飞',
            '處': '处', '專': '专', '將': '将', '書': '书', '號': '号',
            '長': '长', '應': '应', '變': '变', '節': '节', '義': '义',
            '連': '连', '錢': '钱', '場': '场', '馬': '马', '顯': '显',
            '親': '亲', '顧': '顾', '語': '语', '頭': '头', '條': '条',
            '鐘': '钟', '鳥': '鸟', '龍': '龙', '齊': '齐'
        }
        
        # 检查文本中是否包含繁体字符
        for char in text:
            if char in trad_chars:
                return True
        
        # 使用正则表达式匹配一些繁体中文特有的Unicode范围
        # 繁体中文常见于Unicode中的一些特定范围
        pattern = r'[\u4E00-\u9FFF]'  # 基本汉字范围
        matches = re.findall(pattern, text)
        
        # 如果匹配到的汉字超过一定数量，并且包含一些典型的繁体字符组合
        if len(matches) > 5:
            trad_patterns = ['這個', '時間', '國家', '經濟', '發展', '關於', '實現', '東西', '學習', '電話']
            for pattern in trad_patterns:
                if pattern in text:
                    return True
        
        return False
    
    @abstractmethod
    def collect_news(self):
        """收集新闻的抽象方法，需要被子类实现"""
        pass 