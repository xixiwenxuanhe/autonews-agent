import requests
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class EconomyNewsAgent(BaseAgent):
    """经济新闻智能体"""
    
    def __init__(self):
        """初始化经济新闻智能体"""
        super().__init__()
        self.categories = ["business"]
        self.en_keywords = [
            # 宏观经济
            "economy", "economic", "GDP", "inflation", "recession", "economic growth", 
            "monetary policy", "fiscal policy", "interest rate", "central bank", 
            "economic forecast", "economic outlook", "economic indicator",
            
            # 金融市场
            "finance", "financial", "market", "stock market", "bond market", 
            "stock exchange", "securities", "equity", "market volatility", 
            "bull market", "bear market", "trading", "derivatives",
            
            # 投资相关
            "investment", "investor", "portfolio", "asset management", "wealth management",
            "hedge fund", "private equity", "venture capital", "mutual fund", "ETF",
            "dividend", "capital gains", "investment strategy", "return on investment",
            
            # 企业财务与运营
            "business", "corporate", "earnings", "revenue", "profit", "loss", 
            "quarterly report", "balance sheet", "income statement", "cash flow",
            "merger", "acquisition", "IPO", "initial public offering", "bankruptcy",
            
            # 国际贸易与关系
            "trade", "tariff", "trade deficit", "trade surplus", "trade war", 
            "global economy", "economic sanctions", "trade agreement", "export", "import",
            "economic cooperation", "economic integration", "globalization",
            
            # 行业与趋势
            "industry", "sector", "retail", "manufacturing", "technology sector", 
            "energy market", "real estate market", "commodities", "oil price", 
            "gold price", "supply chain", "labor market", "employment", "unemployment"
        ]
        
        self.zh_keywords = [
            # 宏观经济
            "经济", "宏观经济", "国民生产总值", "GDP", "通货膨胀", "通胀", "经济衰退", 
            "经济增长", "货币政策", "财政政策", "利率", "央行", "中央银行", 
            "经济预测", "经济展望", "经济指标", "经济数据",
            
            # 金融市场
            "金融", "金融市场", "股市", "债券市场", "证券交易所", "证券", "股权", 
            "市场波动", "牛市", "熊市", "交易", "衍生品", "期货", "期权",
            
            # 投资相关
            "投资", "投资者", "投资组合", "资产管理", "财富管理", "对冲基金", 
            "私募股权", "风险投资", "共同基金", "交易所交易基金", "分红", 
            "资本收益", "投资策略", "投资回报", "理财",
            
            # 企业财务与运营
            "商业", "企业", "盈利", "营收", "利润", "亏损", "季度报告", "资产负债表", 
            "利润表", "现金流", "并购", "首次公开募股", "IPO", "破产", "公司财报",
            
            # 国际贸易与关系
            "贸易", "关税", "贸易逆差", "贸易顺差", "贸易战", "全球经济", "经济制裁", 
            "贸易协议", "出口", "进口", "经济合作", "经济一体化", "全球化",
            
            # 行业与趋势
            "产业", "行业", "零售业", "制造业", "科技行业", "能源市场", "房地产市场", 
            "大宗商品", "油价", "金价", "供应链", "劳动力市场", "就业", "失业", 
            "数字经济", "共享经济", "平台经济", "经济转型"
        ]
    
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 获取{lang_label}经济新闻...")
        
        # 导入随机模块
        import random
        
        # 随机打乱关键词顺序
        shuffled_keywords = keywords.copy()
        random.shuffle(shuffled_keywords)
        
        # 只选取前30个关键词，避免过多查询
        selected_keywords = shuffled_keywords[:30]
        
        # 将关键词分批处理，每批最多10个关键词
        batch_size = 10
        keywords_batches = [selected_keywords[i:i + batch_size] for i in range(0, len(selected_keywords), batch_size)]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 从{len(keywords)}个关键词中随机选择{len(selected_keywords)}个，分为{len(keywords_batches)}批进行查询")
        
        # 构建NewsAPI请求URL
        base_url = "https://newsapi.org/v2/everything"
        
        # 存储所有批次获取的文章
        all_articles = []
        
        # 设置提前终止条件：获取到12篇文章就停止
        early_stop_count = 12
        
        # 按批次获取文章
        for i, batch_keywords in enumerate(keywords_batches):
            # 构建查询关键词
            query = " OR ".join(batch_keywords)
            
            # 设置请求参数
            params = {
                "apiKey": self.news_api_key,
                "q": query,
                "from": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                "language": language,
                "sortBy": "relevancy",
                "pageSize": 4  # 每批次获取固定数量的文章
            }
            
            try:
                # 发送请求
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # 获取文章列表
                batch_articles = data.get("articles", [])
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 批次 {i+1}/{len(keywords_batches)}: 获取到 {len(batch_articles)} 篇文章")
                
                # 将该批次的文章添加到总文章列表中
                all_articles.extend(batch_articles)
                
                # 如果已经获取足够多的文章，可以提前退出
                if len(all_articles) >= early_stop_count:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 已获取足够多的文章 ({len(all_articles)} 篇)，停止查询")
                    break
                    
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 获取{lang_label}经济新闻批次 {i+1} 失败: {e}")
        
        # 去除可能的重复文章（基于URL）
        unique_articles = []
        seen_urls = set()
        
        for article in all_articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 去重后共 {len(unique_articles)} 篇{lang_label}文章")
        
        # 使用LLM筛选最相关的文章
        if unique_articles:
            return self._filter_relevant_articles(unique_articles, max_articles, lang_label)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 未获取到{lang_label}文章")
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