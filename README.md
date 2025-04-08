# NewsMailAgent 📰✉️

## 🌟 功能特点

- 🔍 自动收集技术、科学和经济领域的最新新闻
- 🌐 支持中英文双语新闻搜索
- 🧠 智能过滤和筛选文章，确保内容相关性
- 🧪 科学领域特别过滤算法，确保排除AI相关内容，专注基础科学研究
- 📊 自动整合新闻内容，生成结构化的简报
- 📧 通过邮件自动发送新闻简报
- ⏰ 支持定时运行，可设置每日自动执行

## 🛠️ 环境配置

### 📦 安装依赖

```bash
pip install -r requirements.txt
```

### ⚙️ 配置环境变量

复制环境变量模板文件并进行配置：

```bash
cp .env.example .env
```

然后编辑`.env`文件，填入您的实际配置：

```
# API密钥配置
NEWS_API_KEY=your_news_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 邮件配置
EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_RECEIVER=recipient@example.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587

# 定时运行配置
SCHEDULE_TIME=07:00
```

各配置项说明：
- 🔑 `NEWS_API_KEY`: 用于获取新闻的API密钥（来自NewsAPI）
- 🔑 `OPENAI_API_KEY`: 用于内容生成和筛选的OpenAI API密钥
- 📨 `EMAIL_SENDER`: 发送新闻简报的邮箱地址
- 🔒 `EMAIL_PASSWORD`: 发送邮箱的密码或应用专用密码
- 📩 `EMAIL_RECEIVER`: 接收新闻简报的邮箱地址
- 🖥️ `SMTP_SERVER`: 邮件服务器地址
- 🔌 `SMTP_PORT`: 邮件服务器端口
- 🕗 `SCHEDULE_TIME`: 定时运行的时间，格式为"HH:MM"

## 📋 使用方法

### 🚀 常规模式运行

```bash
python main.py
```

此命令将启动新闻聚合系统，使用LLM动态生成关键词组合进行搜索，然后整合内容并发送邮件。

### 🔍 使用硬编码关键词运行

```bash
python main.py --hard=true
```

使用`--hard=true`参数会启用硬编码的关键词对进行搜索，并打印详细的搜索结果，便于观察实际获取的文章内容。该模式下系统仍会正常执行内容整合和邮件发送流程。


参数说明：
- 🔄 `--hard=true`: 使用硬编码的关键词对并打印结果
- 📃 `--show_content`: 显示文章摘要
- 🏷️ `--domains`: 指定要搜索的领域，例如：`--domains technology science`
- 🔢 `--num_pairs`: 每个领域每种语言的关键词对数量
- 📊 `--max_articles`: 每个领域每种语言最多保留的文章数量

## 📁 项目结构

```
/
├── agents/                # 智能代理模块
│   ├── base_agent.py     # 基础代理类
│   ├── search_agent.py   # 搜索代理
│   ├── integration_agent.py # 内容整合代理
│   ├── email_agent.py    # 邮件发送代理
│   └── keywords.json     # 预设关键词库
├── main.py               # 主程序入口
├── .env.example          # 环境变量配置模板
├── .env                  # 环境变量配置（需自行创建）
└── requirements.txt      # 项目依赖
```

## 🔧 高级功能

### 🔤 关键词定制

您可以通过修改`agents/keywords.json`文件来自定义各领域的预设关键词，系统会基于这些关键词智能组合搜索查询。

### 🎯 自定义领域提示词

`search_agent.py`中的`domain_prompts`字典定义了各领域的筛选标准，可以根据需要调整筛选偏好。

### 🧬 科学领域AI内容过滤

系统为科学领域特别实现了AI内容过滤机制，确保科学新闻聚焦于物理、生物、化学等基础学科，而非AI应用。

## ❓ 故障排除

如果遇到"API密钥未提供"错误，请检查`.env`文件是否正确配置并被加载。

如果遇到新闻搜索结果不理想：
- 🔍 尝试使用`--hard=true`参数运行
- 📝 检查`keywords.json`文件中的关键词是否适合您的需求
- 🔧 调整`search_agent.py`中的`domain_prompts`

## 📄 许可证

[MIT License](LICENSE)
