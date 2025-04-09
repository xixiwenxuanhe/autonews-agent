import os
import json
import random
import requests
import datetime
from collections import defaultdict
from typing import List, Dict, Any, Tuple

from .base_agent import BaseAgent


class SearchAgent(BaseAgent):
    def __init__(self, api_key=None, domains=None, seed=None):
        """
        初始化搜索代理
        
        Args:
            api_key: 新闻API的密钥
            domains: 要搜索的领域列表，默认为["technology", "science", "economy"]
            seed: 随机种子，用于复现结果
        """
        super().__init__()
        self.api_key = api_key or self.news_api_key
        if not self.api_key:
            raise ValueError("API密钥未提供，请设置NEWS_API_KEY环境变量或在初始化时提供")
            
        self.domains = domains or ["technology", "science", "economy"]
        
        # 设置随机种子以便结果可复现
        if seed:
            random.seed(seed)
            
        # 加载关键词文件
        self.keywords_file = os.path.join(os.path.dirname(__file__), "keywords.json")
        with open(self.keywords_file, 'r', encoding='utf-8') as f:
            self.keywords_data = json.load(f)
        
        # 存储最终结果的变量
        self.collected_articles = {}
        
        # 存储预先生成的关键词对
        self.prepared_keywords = {}
        
        # 硬编码的关键词对，确保科学领域获取物理、生物、化学相关文章
        self.hard_coded_keywords = {
            "technology": {
                "en": [
                    ["software development", "programming language"],
                    ["cybersecurity", "data privacy"],
                    ["internet of things", "smart devices"],
                    ["virtual reality", "augmented reality"]
                ],
                "zh": [
                    ["区块链", "加密货币"],
                    ["5G", "通信技术"],
                    ["自动驾驶", "智能交通"],
                    ["云计算", "边缘计算"]
                ]
            },
            "science": {
                "en": [
                    ["biology", "genetics"],
                    ["chemistry", "molecular structure"],
                    ["biochemistry", "enzymes"],
                    ["astronomy", "astrophysics"]
                ],
                "zh": [
                    ["生物学", "基因研究"],
                    ["化学", "分子结构"],
                    ["生物化学", "蛋白质研究"],
                    ["天文学", "宇宙探索"]
                ]
            },
            "economy": {
                "en": [
                    ["stock market", "investment"],
                    ["central bank", "monetary policy"],
                    ["inflation", "interest rates"],
                    ["trade agreement", "global commerce"]
                ],
                "zh": [
                    ["股市", "投资策略"],
                    ["央行", "货币政策"],
                    ["通货膨胀", "利率调整"],
                    ["贸易协定", "国际贸易"]
                ]
            }
        }
        
        # 定义领域对应的提示语
        self.domain_prompts = {
            "technology": """
                你是一位技术新闻筛选专家。请选择最重要和最具影响力的技术新闻文章。
                优先考虑与人工智能、机器学习、大型语言模型、自然语言处理和计算机视觉相关的突破性新闻。
                其他技术创新如软件开发、硬件技术、云计算、数据科学、区块链、元宇宙、VR/AR、物联网、5G/6G等也属于技术类别。
                请确保所选文章涵盖重大技术突破、行业动态和可能改变行业未来的重要事件。
            """,
            "science": """
                你是一位科学新闻筛选专家。请选择最重要和最具影响力的科学研究文章。
                优先考虑生物学、化学、生物化学、天文学、地球科学和环境科学方面的重大科学发现和突破。
                特别注意：请勿选择物理学、量子物理、人工智能、计算机技术及相关内容的文章。
                经验表明，物理学相关文章容易包含AI和计算机技术内容，应予以排除。
                请确保所选文章涵盖对人类知识有重大贡献的基础研究领域的重要发现，特别是生物学和化学领域。
            """,
            "economy": """
                你是一位经济新闻筛选专家。请选择最重要和最具影响力的经济新闻文章。
                经济新闻主要涵盖股市、金融投资、宏观经济政策、贸易关系、企业盈利和企业并购等内容。
                请不要选择来自技术领域的新闻，即使它们可能对经济有影响。
                关注传统金融内容，如股价变动、央行政策、通胀数据、GDP增长、贸易协议等内容。
            """
        }
    
    def prepare_all_keywords(self, num_keyword_pairs=4, hard=False):
        """
        一次性为所有领域预先生成关键词对
        
        Args:
            num_keyword_pairs: 每个领域每种语言选择的关键词对数量
            hard: 是否使用硬编码的关键词对
        
        Returns:
            Dict: 按领域和语言分类的关键词对
        """
        print("开始为所有领域预生成关键词对...")
        
        for domain in self.domains:
            print(f"\n为{domain}领域选择关键词...")
            
            if hard:
                # 使用硬编码的关键词对
                keyword_pairs = self.hard_coded_keywords[domain]
                print("使用硬编码的关键词对...")
            else:
                # 同时获取中英文关键词对
                keyword_pairs = self._select_bilingual_keyword_pairs(domain, num_keyword_pairs)
            
            # 存储结果
            self.prepared_keywords[domain] = keyword_pairs
            
            # 打印结果
            print(f"- 英文关键词对：")
            for i, pair in enumerate(keyword_pairs["en"]):
                print(f"  {i+1}. {pair[0]} AND {pair[1]}")
                
            print(f"- 中文关键词对：")
            for i, pair in enumerate(keyword_pairs["zh"]):
                print(f"  {i+1}. {pair[0]} AND {pair[1]}")
        
        print("\n所有关键词对已预生成完毕！")
        return self.prepared_keywords
    
    def collect_news(self, num_keyword_pairs=4, max_articles_per_language=10, use_prepared_keywords=True, hard=False):
        """
        收集各个领域的新闻
        
        Args:
            num_keyword_pairs: 每个领域每种语言选择的关键词对数量
            max_articles_per_language: 每个领域每种语言最多保留的文章数量
            use_prepared_keywords: 是否使用预先生成的关键词对
            hard: 是否使用硬编码的关键词对
        
        Returns:
            Dict: 按领域分类的新闻文章
        """
        results = defaultdict(list)
        
        # 如果需要使用预生成的关键词对但还没有生成，则先生成
        if use_prepared_keywords and not self.prepared_keywords:
            self.prepare_all_keywords(num_keyword_pairs, hard)
        
        for domain in self.domains:
            print(f"正在收集{domain}领域的新闻...")
            
            # 获取关键词对（使用预生成的或重新生成）
            if use_prepared_keywords and domain in self.prepared_keywords:
                keyword_pairs = self.prepared_keywords[domain]
            elif hard:
                # 使用硬编码的关键词对
                keyword_pairs = self.hard_coded_keywords[domain]
            else:
                # 为每个领域同时选择中英文关键词对
                keyword_pairs = self._select_bilingual_keyword_pairs(domain, num_keyword_pairs)
            
            # 收集英文新闻
            en_articles = self._collect_domain_news(domain, "en", keyword_pairs["en"])
            
            # 收集中文新闻
            zh_articles = self._collect_domain_news(domain, "zh", keyword_pairs["zh"])
            
            # 分别处理英文和中文文章
            filtered_en_articles = self._process_language_articles(en_articles, domain, "en", max_articles_per_language)
            filtered_zh_articles = self._process_language_articles(zh_articles, domain, "zh", max_articles_per_language)
            
            # 合并结果并打印简要信息
            domain_articles = filtered_en_articles + filtered_zh_articles
            print(f"{domain}领域搜索结果：共{len(domain_articles)}篇文章（英文{len(filtered_en_articles)}篇，中文{len(filtered_zh_articles)}篇）")
            
            # 保存结果
            results[domain] = domain_articles
            self.collected_articles[domain] = domain_articles
        
        # 如果使用硬编码关键词，则自动打印结果
        if hard:
            print("\n===== 搜索结果 =====")
            self.print_search_results(show_content=False)
            
        return results
    
    def _select_bilingual_keyword_pairs(self, domain: str, num_pairs: int) -> Dict[str, List[List[str]]]:
        """
        同时使用LLM为中英文选择多样化的关键词对
        
        Args:
            domain: 领域名称
            num_pairs: 每种语言要选择的关键词对数量
        
        Returns:
            Dict[str, List[List[str]]]: 按语言分类的关键词对字典
        """
        # 获取英文和中文关键词
        en_keywords = self.keywords_data[domain]["en"]
        zh_keywords = self.keywords_data[domain]["zh"]
        
        # 将关键词展平为列表
        en_flat_keywords = [word for pair in en_keywords for word in pair]
        zh_flat_keywords = [word for pair in zh_keywords for word in pair]
        
        # 为不同领域构建不同的提示词指导
        domain_guidance = ""
        if domain == "technology":
            domain_guidance = """
            技术领域包含多个不同的子领域，请确保选择的关键词对覆盖不同技术方向，使搜索结果多样化。
            请确保每组关键词对属于不同的子领域，不要选择语义相近的多组。
            特别注意：中文和英文关键词绝对不能有对应关系，必须选择完全不同的子领域。
            例如：如果英文选择了"artificial intelligence/machine learning"相关主题，中文就不能选择"人工智能/机器学习"，而应该选择"区块链/云计算"等完全不同的技术领域。
            """
        elif domain == "science":
            domain_guidance = """
            科学领域包含多个不同的学科，请确保选择的关键词对覆盖不同科学领域，使搜索结果多样化。
            请确保每组关键词对属于不同的学科，尽量覆盖多个科学分支。
            特别注意：中文和英文关键词必须完全不相关，绝对不能选择相同的学科领域。
            例如：如果英文选择了"physics/quantum"相关主题，中文就不能选择"物理/量子"，而应该选择"生物学/基因"等完全不同的科学领域。
            """
        else:  # economy
            domain_guidance = """
            经济领域包含多个不同的方面，请确保关键词覆盖不同经济方向，使搜索结果多样化。
            请确保每组关键词对关注经济的不同方面，避免重复或相似的主题。
            特别注意：中文和英文关键词必须完全不相关，绝对不能有任何对应关系。
            例如：如果英文选择了"stock market/investment"相关主题，中文就不能选择"股市/投资"，而应该选择"宏观经济/国际贸易"等完全不同的经济领域。
            """
        
        # 准备提示语
        prompt = f"""
        请为{domain}领域同时选择中英文搜索关键词对。

        以下是{domain}领域的英文关键词列表:
        {en_flat_keywords}
        
        以下是{domain}领域的中文关键词列表:
        {zh_flat_keywords}
        
        {domain_guidance}
        
        请从上述列表中分别为英文和中文各选择{num_pairs}组关键词对，每组包含2个关键词。请确保:
        1. 每组内的关键词彼此相关，能够组合形成有效的搜索查询
        2. 不同组之间要覆盖{domain}领域的不同方面，确保多样性
        3. 避免不同组之间的关联性过高，以减少搜索结果的重复
        4. 【最重要】中文和英文关键词必须选择完全不同的方面，绝对不能出现翻译对应关系
           - 错误示例：英文选"AI/machine learning"，中文选"人工智能/机器学习"
           - 正确示例：英文选"AI/machine learning"，中文选"区块链/元宇宙"

        这样做的目的是最大化信息覆盖面，确保不会因语言重复而错过重要信息。
        
        请按以下格式回复:
        {{
          "en": [
            ["英文关键词1", "英文关键词2"],
            ["英文关键词3", "英文关键词4"],
            ...
          ],
          "zh": [
            ["中文关键词1", "中文关键词2"],
            ["中文关键词3", "中文关键词4"],
            ...
          ]
        }}
        """
        
        # 调用LLM API获取关键词对
        response = self.call_llm_api(prompt)
        response_text = response.strip()
        
        # 找到JSON部分
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        # 解析JSON
        json_str = response_text[start_idx:end_idx]
        selected_pairs = json.loads(json_str)
        
        # 确保每对都有2个关键词
        en_valid_pairs = [pair for pair in selected_pairs["en"] if len(pair) == 2]
        zh_valid_pairs = [pair for pair in selected_pairs["zh"] if len(pair) == 2]
        
        # 构建并返回结果
        return {
            "en": en_valid_pairs[:num_pairs],
            "zh": zh_valid_pairs[:num_pairs]
        }
    
    def _process_language_articles(self, articles: List[Dict], domain: str, language: str, max_articles: int) -> List[Dict]:
        """
        处理特定语言的文章
        
        Args:
            articles: 文章列表
            domain: 领域名称
            language: 语言代码
            max_articles: 最大文章数量
        
        Returns:
            List[Dict]: 处理后的文章列表
        """
        # 简化输出，只显示一行汇总信息
        article_count = len(articles)
        
        # 首先去重
        unique_articles = self._remove_duplicates(articles)
        
        # 如果文章数量不足，直接返回
        if len(unique_articles) <= max_articles:
            formatted_articles = self._format_articles(unique_articles)
            return formatted_articles
        
        # 筛选
        filtered_articles = self._filter_relevant_articles(unique_articles, domain, max_articles)
        
        # 格式化
        formatted_articles = self._format_articles(filtered_articles)
        
        return formatted_articles
    
    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """
        移除重复的文章
        
        Args:
            articles: 文章列表
        
        Returns:
            List[Dict]: 去重后的文章列表
        """
        if not articles:
            return []
            
        # 使用URL作为唯一标识
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            url = article.get('url', '')
            
            # 只保留URL未见过的文章
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
            
            # 如果URL为空，使用标题+来源作为备用标识
            elif not url:
                title = article.get('title', '')
                source = article.get('source', {}).get('name', '')
                key = f"{title}_{source}"
                
                if key and key not in seen_urls:
                    seen_urls.add(key)
                    unique_articles.append(article)
                
        return unique_articles
    
    def _collect_domain_news(self, domain: str, language: str, keyword_pairs: List[List[str]]) -> List[Dict]:
        """
        收集特定领域和语言的新闻
        
        Args:
            domain: 领域名称
            language: 语言代码 ('en' 或 'zh')
            keyword_pairs: 关键词对列表
        
        Returns:
            List[Dict]: 收集到的新闻文章列表
        """
        collected_articles = []
        
        # 根据语言设置API参数
        language_param = 'en' if language == 'en' else 'zh'
        
        # 获取当前日期和7天前的日期，提高信息时效性
        today = datetime.date.today()
        week_ago = today - datetime.timedelta(days=7)
        
        # 为每对关键词执行搜索
        for keyword_pair in keyword_pairs:
            # 构造查询字符串（两个关键词之间用AND连接）
            query = " AND ".join(keyword_pair)
            
            # 科学领域添加简单的负面关键词（排除词）
            if domain == "science":
                # 通用排除词 - 简化为最常见的几个
                exclude_words = ["AI", "artificial intelligence", "physics", "quantum", "物理", "人工智能"]
                
                # 添加NOT运算符
                for word in exclude_words:
                    query += f" NOT {word}"
            
            # 构造API请求
            params = {
                'apiKey': self.api_key,
                'q': query,
                'language': language_param,
                'from': week_ago.isoformat(),
                'to': today.isoformat(),
                'sortBy': 'publishedAt',  # 按发布时间排序，优先获取最新内容
                'pageSize': 5,  # 每对关键词最多获取5篇文章
            }
                
            response = requests.get('https://newsapi.org/v2/everything', params=params)
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                
                # 简单打印获取到的文章
                for i, article in enumerate(articles):
                    title = article.get('title', 'No title')
                    print(f"  {i+1}. {title}")
                
                # 为每篇文章添加领域和关键词信息
                for article in articles:
                    article['domain'] = domain
                    article['search_keywords'] = keyword_pair
                    article['language'] = 'en' if language == 'en' else 'zh'
                    collected_articles.append(article)
            else:
                error_msg = data.get('message', '未知错误')
                print(f"API响应错误: {error_msg}")
                
            # 简单的延迟，以避免API速率限制
            import time
            time.sleep(1)
                
        return collected_articles
    
    def _filter_relevant_articles(self, articles: List[Dict], domain: str, max_articles: int) -> List[Dict]:
        """
        使用LLM筛选最相关的文章
        
        Args:
            articles: 候选文章列表
            domain: 领域名称
            max_articles: 最大文章数量
        
        Returns:
            List[Dict]: 筛选后的文章列表
        """
        if len(articles) <= max_articles:
            return articles
            
        # 准备文章摘要列表
        article_summaries = []
        for i, article in enumerate(articles):
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            summary = f"#{i+1}: {title}\n{description}\n"
            article_summaries.append(summary)
            
        # 构造提示语
        prompt = f"""
        {self.domain_prompts[domain]}
        
        以下是{domain}领域的新闻文章列表:
        
        {"".join(article_summaries)}
        
        请从上述列表中选择{max_articles}篇最重要和最相关的文章。
        选择时请考虑文章的多样性，覆盖不同的子领域和内容，避免选择过于相似的内容。
        请按重要性排序，仅返回文章编号，格式如下:
        [1, 5, 8, ...]
        """
        
        # 调用LLM API筛选文章
        response = self.call_llm_api(prompt, temperature=0.3)
        response_text = response.strip()
        
        # 提取JSON数组
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']') + 1
        json_str = response_text[start_idx:end_idx]
        selected_indices = json.loads(json_str)
        
        # 验证并调整索引
        valid_indices = []
        for idx in selected_indices:
            # 将1-based索引转换为0-based索引
            adjusted_idx = idx - 1
            if 0 <= adjusted_idx < len(articles):
                valid_indices.append(adjusted_idx)
                
        # 选择文章
        filtered_articles = [articles[i] for i in valid_indices[:max_articles]]
        return filtered_articles
    
    def _format_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        格式化文章以便后续处理
        
        Args:
            articles: 文章列表
        
        Returns:
            List[Dict]: 格式化后的文章列表
        """
        formatted_articles = []
        
        for article in articles:
            # 提取关键字段
            formatted = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', ''),
                'publishedAt': article.get('publishedAt', ''),
                'domain': article.get('domain', ''),
                'language': '英文' if article.get('language') == 'en' else '中文',
                'keywords': article.get('search_keywords', [])
            }
                
            formatted_articles.append(formatted)
            
        return formatted_articles
    
    def print_search_results(self, show_content=False):
        """
        打印搜索结果
        
        Args:
            show_content: 是否显示文章内容，默认为False
        """
        if not self.collected_articles:
            print("尚未收集任何文章，请先调用collect_news方法。")
            return
        
        for domain, articles in self.collected_articles.items():
            print(f"\n{'='*20} {domain.upper()} 领域新闻 ({len(articles)}篇) {'='*20}")
            
            # 按语言分组
            en_articles = [a for a in articles if a['language'] == '英文']
            zh_articles = [a for a in articles if a['language'] == '中文']
            
            print(f"\n--- 英文文章 ({len(en_articles)}篇) ---")
            for i, article in enumerate(en_articles):
                print(f"{i+1}. {article['title']}")
                print(f"   来源: {article['source']} | 发布时间: {article['publishedAt']}")
                print(f"   关键词: {' AND '.join(article['keywords'])}")
                print(f"   URL: {article['url']}")
                if show_content and article['description']:
                    print(f"   摘要: {article['description']}")
                print()
                
            print(f"\n--- 中文文章 ({len(zh_articles)}篇) ---")
            for i, article in enumerate(zh_articles):
                print(f"{i+1}. {article['title']}")
                print(f"   来源: {article['source']} | 发布时间: {article['publishedAt']}")
                print(f"   关键词: {' AND '.join(article['keywords'])}")
                print(f"   URL: {article['url']}")
                if show_content and article['description']:
                    print(f"   摘要: {article['description']}")
                print()


if __name__ == "__main__":
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="新闻搜索代理")
    parser.add_argument("--domains", type=str, nargs="+", default=["technology", "science", "economy"], 
                        help="要搜索的领域，可选：technology, science, economy")
    parser.add_argument("--num_pairs", type=int, default=4, help="每个领域每种语言的关键词对数量")
    parser.add_argument("--max_articles", type=int, default=5, help="每个领域每种语言保留的文章数量")
    parser.add_argument("--show_content", action="store_true", help="是否显示文章摘要")
    parser.add_argument("--hard", action="store_true", help="是否使用硬编码的关键词对，并打印搜索结果")
    
    args = parser.parse_args()
    
    # 创建搜索代理实例
    agent = SearchAgent(domains=args.domains)
    
    # 预先生成所有领域的关键词对
    print("===== 预生成所有领域的关键词对 =====")
    agent.prepare_all_keywords(num_keyword_pairs=args.num_pairs, hard=args.hard)
    
    # 使用预生成的关键词对收集新闻
    print("\n===== 使用预生成的关键词对收集新闻 =====")
    results = agent.collect_news(num_keyword_pairs=args.num_pairs, 
                               max_articles_per_language=args.max_articles, 
                               use_prepared_keywords=True,
                               hard=args.hard)
    
    # 如果使用硬编码关键词，则自动打印结果
    if args.hard:
        print("\n===== 搜索结果 =====")
        agent.print_search_results(show_content=args.show_content)


