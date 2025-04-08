import requests
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class TechNewsAgent(BaseAgent):
    """IT科技新闻智能体"""
    
    def __init__(self):
        """初始化IT科技新闻智能体"""
        super().__init__()
        self.categories = ["technology", "science"]
        self.keywords = ["AI", "artificial intelligence", "tech", "technology", 
                        "digital", "software", "hardware", "innovation"]
    
    def collect_news(self, max_articles=5):
        """收集IT科技相关新闻
        
        Args:
            max_articles (int): 最大文章数量
            
        Returns:
            list: 新闻文章列表
        """
        # 获取当前日期和前一天的日期
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        from_date = yesterday.strftime('%Y-%m-%d')
        
        # 构建NewsAPI请求URL
        base_url = "https://newsapi.org/v2/everything"
        
        # 构建查询关键词
        query = " OR ".join(self.keywords)
        
        # 设置请求参数
        params = {
            "apiKey": self.news_api_key,
            "q": query,
            "from": from_date,
            "language": "en",
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
                return self._filter_relevant_articles(articles, max_articles)
            else:
                return []
                
        except Exception as e:
            print(f"获取IT科技新闻失败: {e}")
            return []
    
    def _filter_relevant_articles(self, articles, max_articles):
        """使用LLM筛选最相关的文章
        
        Args:
            articles (list): 原始文章列表
            max_articles (int): 最大返回文章数量
            
        Returns:
            list: 筛选后的文章列表
        """
        # 如果文章数量少于max_articles，直接返回所有文章
        if len(articles) <= max_articles:
            return self._format_articles(articles)
        
        # 构建提示词
        article_summaries = []
        for i, article in enumerate(articles[:10]):  # 只处理前10篇文章
            title = article.get("title", "无标题")
            description = article.get("description", "无描述")
            article_summaries.append(f"{i+1}. 标题: {title}\n   描述: {description}")
        
        article_text = "\n\n".join(article_summaries)
        
        prompt = f"""你是一个专业的IT科技新闻编辑，请从以下IT科技新闻中选择{max_articles}篇最重要、最有影响力的文章，它们应该涵盖重要技术突破、产业动态或具有广泛影响的IT新闻。
        
新闻列表:
{article_text}

请只返回你选择的文章序号，格式为逗号分隔的数字，例如: 1,3,5
"""
        
        # 调用LLM API
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
            return self._format_articles(selected_articles)
            
        except Exception as e:
            print(f"解析LLM响应失败: {e}")
            # 出错时返回前max_articles篇文章
            return self._format_articles(articles[:max_articles])
    
    def _format_articles(self, articles):
        """格式化文章为统一输出格式
        
        Args:
            articles (list): 原始文章列表
            
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
                "category": "IT科技"
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles 