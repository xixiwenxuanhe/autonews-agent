import requests
from datetime import datetime, timedelta
from .base_agent import BaseAgent

class ScienceNewsAgent(BaseAgent):
    """科学新闻智能体"""
    
    def __init__(self):
        """初始化科学新闻智能体"""
        super().__init__()
        self.categories = ["science"]
        self.en_keywords = [
            # 基础科学领域
            "science", "scientific discovery", "scientific research", "laboratory", "experiment",
            "scientific breakthrough", "scientific innovation", "scientific theory",
            "scientific study", "scientific method", "scientific evidence", "scientists",
            
            # 生命科学
            "biology", "biological", "microbiology", "molecular biology", "genetics", 
            "genomics", "DNA", "RNA", "protein", "cell biology", "evolutionary biology",
            "ecology", "biodiversity", "ecosystem", "species", "conservation biology",
            
            # 医学与健康
            "medicine", "medical research", "medical breakthrough", "health science", 
            "clinical trial", "drug discovery", "pharmaceutical", "disease", "vaccine",
            "pathogen", "immunology", "epidemiology", "public health", "global health",
            
            # 生物技术
            "biotech", "biotechnology", "genetic engineering", "CRISPR", "gene editing",
            "synthetic biology", "bioinformatics", "biomaterials", "biofuel", 
            "biomedical engineering", "tissue engineering", "stem cells",
            
            # 物理学
            "physics", "astrophysics", "particle physics", "quantum physics", "quantum mechanics",
            "theoretical physics", "nuclear physics", "plasma physics", "condensed matter physics",
            "relativity", "dark matter", "dark energy", "gravitational waves",
            
            # 化学
            "chemistry", "biochemistry", "chemical", "organic chemistry", "inorganic chemistry",
            "analytical chemistry", "physical chemistry", "polymer", "catalyst", "molecule",
            "reaction", "synthesis", "nanomaterials", "electrochemistry",
            
            # 地球与环境科学
            "earth science", "geology", "geophysics", "meteorology", "climatology", 
            "oceanography", "atmospheric science", "environmental science", "climate change",
            "global warming", "carbon emissions", "sustainability", "renewable energy",
            
            # 太空科学
            "astronomy", "space science", "cosmology", "planet", "solar system", "galaxy",
            "universe", "NASA", "space exploration", "space telescope", "exoplanet",
            "mars mission", "space station", "satellite", "rocket", "spacecraft"
        ]
        
        self.zh_keywords = [
            # 基础科学领域
            "科学", "科学发现", "科学研究", "实验室", "实验", "科学突破", "科学创新", 
            "科学理论", "科学研究", "科学方法", "科学证据", "科学家", "院士",
            
            # 生命科学
            "生物学", "生物", "微生物学", "分子生物学", "遗传学", "基因组学", 
            "DNA", "RNA", "蛋白质", "细胞生物学", "进化生物学", "生态学", 
            "生物多样性", "生态系统", "物种", "保护生物学",
            
            # 医学与健康
            "医学", "医学研究", "医学突破", "健康科学", "临床试验", "药物发现", 
            "制药", "疾病", "疫苗", "病原体", "免疫学", "流行病学", "公共卫生", "全球健康",
            
            # 生物技术
            "生物技术", "基因工程", "基因编辑", "CRISPR", "合成生物学", "生物信息学", 
            "生物材料", "生物燃料", "生物医学工程", "组织工程", "干细胞",
            
            # 物理学
            "物理学", "天体物理学", "粒子物理学", "量子物理学", "量子力学", "理论物理学", 
            "核物理学", "等离子体物理学", "凝聚态物理学", "相对论", "暗物质", "暗能量", "引力波",
            
            # 化学
            "化学", "生物化学", "有机化学", "无机化学", "分析化学", "物理化学", 
            "聚合物", "催化剂", "分子", "化学反应", "合成", "纳米材料", "电化学",
            
            # 地球与环境科学
            "地球科学", "地质学", "地球物理学", "气象学", "气候学", "海洋学", 
            "大气科学", "环境科学", "气候变化", "全球变暖", "碳排放", "可持续发展", "可再生能源",
            
            # 太空科学
            "天文学", "太空科学", "宇宙学", "行星", "太阳系", "银河系", "宇宙", 
            "航天", "太空探索", "天文望远镜", "系外行星", "火星任务", "空间站", "卫星", "火箭", "宇宙飞船"
        ]
    
    def collect_news(self, max_articles=5):
        """收集科学相关新闻，包括中英文各5条
        
        Args:
            max_articles (int): 每种语言的最大文章数量
            
        Returns:
            list: 新闻文章列表
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 收集科学新闻...")
        
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
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 已过滤 {filtered_count} 条繁体中文新闻")
        
        # 确保不超过max_articles数量
        simplified_chinese_news = simplified_chinese_news[:max_articles]
        
        # 合并结果
        combined_news = english_news + simplified_chinese_news
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 收集完成: {len(combined_news)} 条 (英:{len(english_news)}, 中:{len(simplified_chinese_news)})")
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 获取{lang_label}科学新闻...")
        
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
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 从{len(keywords)}个关键词中随机选择{len(selected_keywords)}个，分为{len(keywords_batches)}批进行查询")
        
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
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 批次 {i+1}/{len(keywords_batches)}: 获取到 {len(batch_articles)} 篇文章")
                
                # 将该批次的文章添加到总文章列表中
                all_articles.extend(batch_articles)
                
                # 如果已经获取足够多的文章，可以提前退出
                if len(all_articles) >= early_stop_count:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 已获取足够多的文章 ({len(all_articles)} 篇)，停止查询")
                    break
                    
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ 获取{lang_label}科学新闻批次 {i+1} 失败: {e}")
        
        # 去除可能的重复文章（基于URL）
        unique_articles = []
        seen_urls = set()
        
        for article in all_articles:
            url = article.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 去重后共 {len(unique_articles)} 篇{lang_label}文章")
        
        # 使用LLM筛选最相关的文章
        if unique_articles:
            return self._filter_relevant_articles(unique_articles, max_articles, lang_label)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 未获取到{lang_label}文章")
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
        
        prompt = f"""你是一个专业的科学新闻编辑，请从以下{language_label}科学新闻中选择{max_articles}篇最重要、最有影响力的文章，它们应该涵盖重要科学发现、研究突破或具有潜在应用价值的科学进展。
        
新闻列表:
{article_text}

请只返回你选择的文章序号，格式为逗号分隔的数字，例如: 1,3,5
"""
        
        # 调用LLM API
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔬 筛选{language_label}文章中...")
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
                "category": "科学",
                "language": language_label
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles 