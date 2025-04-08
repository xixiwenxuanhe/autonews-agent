import random
from datetime import datetime
from .base_agent import BaseAgent

class ContentIntegrationAgent(BaseAgent):
    """内容整合智能体"""
    
    def __init__(self):
        """初始化内容整合智能体"""
        super().__init__()
        self.inspirational_quotes = [
            "创新是区分领导者和跟随者的特质。 - 史蒂夫·乔布斯",
            "知识就是力量。 - 弗朗西斯·培根",
            "学习是一种永无止境的旅程。 - 不详",
            "成功不是最终的，失败也不是致命的，重要的是继续前进的勇气。 - 温斯顿·丘吉尔",
            "每一个不曾起舞的日子，都是对生命的辜负。 - 尼采",
            "世上最遥远的距离不是生与死，而是我站在你面前，你却不知道我爱你。 - 泰戈尔",
            "生活中最重要的事情是要有一个远大的目标，并有决心去实现它。 - 约翰·洛克菲勒",
            "科技的进步在于取代那些能够被理性描述的工作。 - 埃隆·马斯克",
            "发现创新不等于创新，创新不等于创业。 - 吴军",
            "每一个伟大的事业都始于一个不合理的假设。 - 彼得·泰尔"
        ]
    
    def collect_news(self):
        """实现抽象方法，内容整合智能体不需要收集新闻，返回空列表即可
        
        Returns:
            list: 空的新闻列表
        """
        return []
    
    def integrate_content(self, tech_news, economy_news, science_news):
        """整合各类新闻内容并生成邮件内容
        
        Args:
            tech_news (list): IT科技新闻列表
            economy_news (list): 经济新闻列表
            science_news (list): 科学新闻列表
            
        Returns:
            str: 整合后的邮件内容
        """
        today = datetime.now().strftime("%Y年%m月%d日")
        
        # 选择一条随机励志名言
        random_quote = random.choice(self.inspirational_quotes)
        
        # 使用大语言模型生成标题
        title_prompt = f"""你是一个专业的新闻编辑，请为今天（{today}）的新闻摘要生成一个简洁有力的标题。
标题应该能吸引读者注意力，并且反映当天的主要新闻内容。
请不要超过20个字，只需要返回标题本身，不要加任何其他内容。"""
        
        title = self.call_llm_api(title_prompt, temperature=0.7) or f"{today} 每日新闻摘要"
        
        # 构建HTML邮件模板
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .date {{
            color: #888;
            font-size: 14px;
        }}
        .quote {{
            font-style: italic;
            text-align: center;
            color: #666;
            margin: 20px 0;
            padding: 10px;
            border-left: 3px solid #ddd;
            background-color: #f9f9f9;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: #444;
            margin-bottom: 15px;
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
        }}
        .news-item {{
            margin-bottom: 20px;
        }}
        .news-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .news-source {{
            font-size: 12px;
            color: #888;
        }}
        .news-description {{
            margin-top: 5px;
        }}
        .news-link {{
            display: inline-block;
            margin-top: 5px;
            color: #0066cc;
            text-decoration: none;
        }}
        .news-link:hover {{
            text-decoration: underline;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #888;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="date">{today}</div>
    </div>
    
    <div class="quote">
        {random_quote}
    </div>
"""

        # 添加IT科技新闻部分
        if tech_news:
            html_content += f"""
    <div class="section">
        <h2 class="section-title">📱 IT科技新闻</h2>
"""
            for news in tech_news:
                html_content += f"""
        <div class="news-item">
            <div class="news-title">{news.get('title', '无标题')}</div>
            <div class="news-source">来源: {news.get('source', '未知来源')}</div>
            <div class="news-description">{news.get('description', '无描述')}</div>
            <a href="{news.get('url', '#')}" class="news-link" target="_blank">阅读更多</a>
        </div>
"""
            html_content += """
    </div>
"""

        # 添加经济新闻部分
        if economy_news:
            html_content += f"""
    <div class="section">
        <h2 class="section-title">💰 经济新闻</h2>
"""
            for news in economy_news:
                html_content += f"""
        <div class="news-item">
            <div class="news-title">{news.get('title', '无标题')}</div>
            <div class="news-source">来源: {news.get('source', '未知来源')}</div>
            <div class="news-description">{news.get('description', '无描述')}</div>
            <a href="{news.get('url', '#')}" class="news-link" target="_blank">阅读更多</a>
        </div>
"""
            html_content += """
    </div>
"""

        # 添加科学新闻部分
        if science_news:
            html_content += f"""
    <div class="section">
        <h2 class="section-title">🔬 科学新闻</h2>
"""
            for news in science_news:
                html_content += f"""
        <div class="news-item">
            <div class="news-title">{news.get('title', '无标题')}</div>
            <div class="news-source">来源: {news.get('source', '未知来源')}</div>
            <div class="news-description">{news.get('description', '无描述')}</div>
            <a href="{news.get('url', '#')}" class="news-link" target="_blank">阅读更多</a>
        </div>
"""
            html_content += """
    </div>
"""

        # 添加页脚
        html_content += f"""
    <div class="footer">
        <p>此邮件由多智能体新闻聚合系统自动生成 - {today}</p>
    </div>
</body>
</html>
"""
        
        return html_content 