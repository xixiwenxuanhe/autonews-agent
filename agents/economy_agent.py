import requests
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class EconomyNewsAgent(BaseAgent):
    """经济新闻智能体"""
    
    def __init__(self):
        """初始化经济新闻智能体"""
        super().__init__()
        self.categories = ["business"]
        self.en_keywords = ["economy", "finance", "market", "stock", "trade", 
                         "business", "economic", "financial", "investment"]
        self.zh_keywords = ["经济", "金融", "市场", "股票", "贸易", "商业", 
                         "投资", "证券", "财经"]
    
    def collect_news(self, max_articles=5):
        """收集经济相关新闻，包括中英文各5条
        
        Args:
            max_articles (int): 每种语言的最大文章数量
            
        Returns:
            list: 新闻文章列表
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 收集经济新闻...")
        
        # 获取当前日期和前一天的日期
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        from_date = yesterday.strftime('%Y-%m-%d')
        
        # 获取英文新闻
        english_news = self._collect_language_news(self.en_keywords, "en", max_articles)
        
        # 获取中文新闻 - 多获取一些以便过滤繁体
        zh_max = max_articles * 2  # 获取更多中文新闻以便过滤繁体
        chinese_news = self._collect_language_news(self.zh_keywords, "zh", zh_max)
        
        # 过滤繁体中文新闻
        simplified_chinese_news = []
        filtered_count = 0
        
        for news in chinese_news:
            # 检查标题和描述是否包含繁体中文
            title = news.get('title', '')
            desc = news.get('description', '')
            
            if self.is_traditional_chinese(title) or self.is_traditional_chinese(desc):
                filtered_count += 1
                continue
            
            simplified_chinese_news.append(news)
            
            # 如果已经收集了足够数量的简体中文新闻，就停止
            if len(simplified_chinese_news) >= max_articles:
                break
        
        if filtered_count > 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 已过滤 {filtered_count} 条繁体中文新闻")
        
        # 确保不超过max_articles数量
        simplified_chinese_news = simplified_chinese_news[:max_articles]
        
        # 合并结果
        combined_news = english_news + simplified_chinese_news
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 收集完成: {len(combined_news)} 条 (英:{len(english_news)}, 中:{len(simplified_chinese_news)})")
        return combined_news
    
    def _collect_language_news(self, keywords, language, max_articles):
        """收集特定语言的新闻
        
        Args:
            keywords (list): 搜索关键词列表
            language (str): 语言代码，'en'为英文，'zh'为中文
            max_articles (int): 最大文章数量
            
        Returns:
            list: 该语言的新闻文章列表
        """
        lang_label = "英文" if language == "en" else "中文"
        # 构建NewsAPI请求URL
        base_url = "https://newsapi.org/v2/everything"
        
        # 构建查询关键词
        query = " OR ".join(keywords)
        
        # 设置请求参数
        params = {
            "apiKey": self.news_api_key,
            "q": query,
            "from": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            "language": language,
            "sortBy": "relevancy",
            "pageSize": max_articles * 2  # 获取更多文章以便筛选
        }
        
        try:
            # 发送请求
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 获取文章列表
            articles = data.get("articles", [])
            
            # 使用LLM筛选最相关的文章
            if articles:
                return self._filter_relevant_articles(articles, max_articles, lang_label)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 未获取到{lang_label}文章")
                return []
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 获取{lang_label}经济新闻失败: {e}")
            return []
    
    def _filter_relevant_articles(self, articles, max_articles, language_label=""):
        """使用LLM筛选最相关的文章
        
        Args:
            articles (list): 原始文章列表
            max_articles (int): 最大返回文章数量
            language_label (str): 语言标签，用于日志
            
        Returns:
            list: 筛选后的文章列表
        """
        # 如果文章数量少于max_articles，直接返回所有文章
        if len(articles) <= max_articles:
            return self._format_articles(articles, language_label)
        
        # 构建提示词
        article_summaries = []
        for i, article in enumerate(articles[:10]):  # 只处理前10篇文章
            title = article.get("title", "无标题")
            description = article.get("description", "无描述")
            article_summaries.append(f"{i+1}. 标题: {title}\n   描述: {description}")
        
        article_text = "\n\n".join(article_summaries)
        
        prompt = f"""你是一个专业的经济金融新闻编辑，请从以下{language_label}经济新闻中选择{max_articles}篇最重要、最有影响力的文章，它们应该涵盖重大经济事件、金融市场动态或具有广泛影响的产业变革。
        
新闻列表:
{article_text}

请只返回你选择的文章序号，格式为逗号分隔的数字，例如: 1,3,5
"""
        
        # 调用LLM API
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 筛选{language_label}文章中...")
        response = self.call_llm_api(prompt, temperature=0.3)
        
        try:
            # 解析响应，获取选中的文章索引
            selected_indices = []
            for item in response.replace(" ", "").split(","):
                if item.isdigit() and 1 <= int(item) <= len(articles):
                    selected_indices.append(int(item) - 1)
            
            # 截取至max_articles
            selected_indices = selected_indices[:max_articles]
            
            # 返回选中的文章
            selected_articles = [articles[i] for i in selected_indices]
            
            return self._format_articles(selected_articles, language_label)
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 解析LLM响应失败: {e}")
            # 出错时返回前max_articles篇文章
            return self._format_articles(articles[:max_articles], language_label)
    
    def _format_articles(self, articles, language_label=""):
        """格式化文章为统一输出格式
        
        Args:
            articles (list): 原始文章列表
            language_label (str): 语言标签
            
        Returns:
            list: 格式化后的文章列表
        """
        formatted_articles = []
        for article in articles:
            formatted_article = {
                "title": article.get("title", "无标题"),
                "description": article.get("description", "无描述"),
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "未知来源"),
                "published_at": article.get("publishedAt", ""),
                "category": "经济",
                "language": language_label
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles 