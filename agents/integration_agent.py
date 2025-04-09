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
    
    def integrate_content(self, tech_news=None, economy_news=None, biology_news=None):
        """整合各类新闻内容并生成邮件内容
        
        Args:
            tech_news: IT科技新闻列表
            economy_news: 经济新闻列表
            biology_news: 仅为向后兼容保留，不再使用
            
        Returns:
            str: 整合后的邮件内容
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 整合新闻内容...")
        
        # 分类中英文新闻
        zh_tech_news = [news for news in tech_news or [] if news.get('language') == '中文']
        en_tech_news = [news for news in tech_news or [] if news.get('language') == '英文']
        
        zh_economy_news = [news for news in economy_news or [] if news.get('language') == '中文']
        en_economy_news = [news for news in economy_news or [] if news.get('language') == '英文']
        
        # 统计各类新闻数量
        total_zh_news = len(zh_tech_news) + len(zh_economy_news)
        total_en_news = len(en_tech_news) + len(en_economy_news)
        
        today = datetime.now().strftime("%Y年%m月%d日")
        
        # 选择一条随机励志名言
        random_quote = random.choice(self.inspirational_quotes)
        
        # 使用大语言模型生成标题
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 生成邮件标题...")
        title_prompt = f"""你是一个专业的新闻编辑，请为今天（{today}）的新闻摘要生成一个简洁有力的标题。
标题应该能吸引读者注意力，并且反映当天的主要新闻内容。
请不要超过20个字，只需要返回标题本身，不要加任何其他内容。"""
        
        title = self.call_llm_api(title_prompt, temperature=0.7) or f"{today} 每日新闻摘要"
        
        # 构建HTML邮件模板
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>{title}</title>
    <style type="text/css">
        /* 重置样式 */
        body, p, h1, h2, h3, h4, h5, h6, table, td, th, div, ul, ol, li {{
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #333333;
            background-color: #f7f7f7;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        table {{
            border-spacing: 0;
            border-collapse: collapse;
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        td {{
            padding: 0;
            vertical-align: top;
        }}
        img {{
            border: 0;
            -ms-interpolation-mode: bicubic;
            display: block;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
            color: #004080;
        }}
        .quote-text {{
            font-style: italic;
            color: #555555;
        }}
        .news-title {{
            color: #222222;
        }}
        .news-source {{
            color: #777777;
        }}
        .news-description {{
            color: #444444;
        }}
        .section-title {{
            color: #222222;
        }}
        .language-title {{
            color: #555555;
        }}
        .footer-text {{
            color: #777777;
        }}
        
        /* 响应式设计 */
        @media only screen and (max-width: 640px) {{
            .container {{
                width: 100% !important;
            }}
            .content {{
                padding: 15px !important;
            }}
            .header {{
                padding: 15px !important;
            }}
            .section-title {{
                font-size: 18px !important;
            }}
            .news-title {{
                font-size: 16px !important;
            }}
            .news-description {{
                font-size: 14px !important;
            }}
        }}
        
        /* 暗黑模式支持 */
        @media (prefers-color-scheme: dark) {{
            body, .body-wrapper {{
                background-color: #222222 !important;
            }}
            .content-wrapper {{
                background-color: #333333 !important;
            }}
            .section-title, .news-title, h1, h2 {{
                color: #ffffff !important;
            }}
            .news-description, .quote-text {{
                color: #cccccc !important;
            }}
            .news-source, .footer-text {{
                color: #999999 !important;
            }}
            .section-divider {{
                border-color: #444444 !important;
            }}
            a {{
                color: #4d9aff !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; width: 100%; background-color: #f7f7f7;">
    <!-- 外容器 -->
    <table border="0" cellpadding="0" cellspacing="0" width="100%" class="body-wrapper">
        <tr>
            <td align="center" style="padding: 20px 0;">
                <!-- 内容容器 -->
                <table border="0" cellpadding="0" cellspacing="0" width="600" class="container" style="background-color: #ffffff; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <!-- 页眉 -->
                    <tr>
                        <td align="center" class="header" style="padding: 25px 30px; border-bottom: 1px solid #eeeeee;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center">
                                        <h1 style="font-size: 24px; font-weight: bold; color: #333333; margin: 0;">{title}</h1>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding-top: 10px;">
                                        <span style="font-size: 14px; color: #888888;">{today}</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 励志名言 -->
                    <tr>
                        <td align="center" style="padding: 20px 30px;">
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f9f9f9; border-left: 3px solid #dddddd;">
                                <tr>
                                    <td align="center" style="padding: 15px;">
                                        <p class="quote-text" style="font-size: 16px;">{random_quote}</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- 内容区域 -->
                    <tr>
                        <td class="content" style="padding: 0 30px 30px 30px;">
"""

        # 添加IT科技新闻部分
        if tech_news:
            html_content += f"""
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" class="section" style="margin-bottom: 25px;">
                                <tr>
                                    <td>
                                        <h2 class="section-title" style="font-size: 20px; font-weight: bold; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #eeeeee;">📱 IT科技新闻</h2>
                                    </td>
                                </tr>
"""
            # 添加中文新闻
            if zh_tech_news:
                html_content += f"""
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <h3 class="language-title" style="font-size: 17px; font-weight: bold; margin: 10px 0 10px 5px;">🇨🇳 早安中国</h3>
                                    </td>
                                </tr>
"""
                for news in zh_tech_news:
                    html_content += f"""
                                <tr>
                                    <td class="news-item" style="padding: 0 0 20px 10px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td>
                                                    <p class="news-title" style="font-size: 17px; font-weight: bold; margin-bottom: 5px;">{news.get('title', '无标题')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <span class="news-source" style="font-size: 12px;">来源: {news.get('source', '未知来源')}</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 5px;">
                                                    <p class="news-description" style="font-size: 15px;">{news.get('description', '无描述')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 8px;">
                                                    <a href="{news.get('url', '#')}" class="news-link" style="display: inline-block; color: #0066cc; font-size: 14px;" target="_blank">阅读更多 →</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
"""
            
            # 添加英文新闻
            if en_tech_news:
                html_content += f"""
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <h3 class="language-title" style="font-size: 17px; font-weight: bold; margin: 10px 0 10px 5px;">🌍 Hello World</h3>
                                    </td>
                                </tr>
"""
                for news in en_tech_news:
                    html_content += f"""
                                <tr>
                                    <td class="news-item" style="padding: 0 0 20px 10px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td>
                                                    <p class="news-title" style="font-size: 17px; font-weight: bold; margin-bottom: 5px;">{news.get('title', '无标题')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <span class="news-source" style="font-size: 12px;">来源: {news.get('source', '未知来源')}</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 5px;">
                                                    <p class="news-description" style="font-size: 15px;">{news.get('description', '无描述')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 8px;">
                                                    <a href="{news.get('url', '#')}" class="news-link" style="display: inline-block; color: #0066cc; font-size: 14px;" target="_blank">阅读更多 →</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
"""
            html_content += """
                            </table>
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 20px;">
                                <tr>
                                    <td class="section-divider" style="border-top: 1px solid #eeeeee; font-size: 1px; height: 1px;">&nbsp;</td>
                                </tr>
                            </table>
"""

        # 添加经济新闻部分
        if economy_news:
            html_content += f"""
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" class="section" style="margin-bottom: 25px;">
                                <tr>
                                    <td>
                                        <h2 class="section-title" style="font-size: 20px; font-weight: bold; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #eeeeee;">💰 经济新闻</h2>
                                    </td>
                                </tr>
"""
            # 添加中文新闻
            if zh_economy_news:
                html_content += f"""
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <h3 class="language-title" style="font-size: 17px; font-weight: bold; margin: 10px 0 10px 5px;">🇨🇳 早安中国</h3>
                                    </td>
                                </tr>
"""
                for news in zh_economy_news:
                    html_content += f"""
                                <tr>
                                    <td class="news-item" style="padding: 0 0 20px 10px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td>
                                                    <p class="news-title" style="font-size: 17px; font-weight: bold; margin-bottom: 5px;">{news.get('title', '无标题')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <span class="news-source" style="font-size: 12px;">来源: {news.get('source', '未知来源')}</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 5px;">
                                                    <p class="news-description" style="font-size: 15px;">{news.get('description', '无描述')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 8px;">
                                                    <a href="{news.get('url', '#')}" class="news-link" style="display: inline-block; color: #0066cc; font-size: 14px;" target="_blank">阅读更多 →</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
"""
            
            # 添加英文新闻
            if en_economy_news:
                html_content += f"""
                                <tr>
                                    <td style="padding-bottom: 5px;">
                                        <h3 class="language-title" style="font-size: 17px; font-weight: bold; margin: 10px 0 10px 5px;">🌍 Hello World</h3>
                                    </td>
                                </tr>
"""
                for news in en_economy_news:
                    html_content += f"""
                                <tr>
                                    <td class="news-item" style="padding: 0 0 20px 10px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                            <tr>
                                                <td>
                                                    <p class="news-title" style="font-size: 17px; font-weight: bold; margin-bottom: 5px;">{news.get('title', '无标题')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td>
                                                    <span class="news-source" style="font-size: 12px;">来源: {news.get('source', '未知来源')}</span>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 5px;">
                                                    <p class="news-description" style="font-size: 15px;">{news.get('description', '无描述')}</p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 8px;">
                                                    <a href="{news.get('url', '#')}" class="news-link" style="display: inline-block; color: #0066cc; font-size: 14px;" target="_blank">阅读更多 →</a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
"""
            html_content += """
                            </table>
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 20px;">
                                <tr>
                                    <td class="section-divider" style="border-top: 1px solid #eeeeee; font-size: 1px; height: 1px;">&nbsp;</td>
                                </tr>
                            </table>
"""

        # 添加页脚
        html_content += f"""
                        </td>
                    </tr>
                    
                    <!-- 页脚 -->
                    <tr>
                        <td align="center" style="padding: 20px 30px; border-top: 1px solid #eeeeee; background-color: #f9f9f9; border-radius: 0 0 5px 5px;">
                            <p class="footer-text" style="font-size: 12px; color: #888888;">此邮件由多智能体新闻聚合系统自动生成 - {today}</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 整合完成 (中文:{total_zh_news}, 英文:{total_en_news})")
        
        return html_content 