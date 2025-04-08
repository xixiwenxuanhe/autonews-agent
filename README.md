# 多智能体新闻聚合系统

这是一个基于多智能体框架设计的新闻聚合系统，可以自动收集IT科技、经济和科学领域的新闻，整合内容并通过邮件发送。

## 系统架构

系统由多个智能体组成，每个智能体负责不同的任务：

1. **IT科技新闻智能体**：负责搜集全球IT、科技、人工智能等相关新闻
2. **经济新闻智能体**：负责搜集全球经济、金融市场等相关新闻
3. **科学新闻智能体**：负责搜集科学研究、技术突破等相关新闻
4. **内容整合智能体**：接收其他智能体提供的内容，进行整合和排版
5. **邮件发送智能体**：负责将整合后的内容通过邮件发送

## 安装说明

1. 克隆仓库到本地
2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 配置说明

在使用前，请确保正确配置`.env`文件，包含以下内容：

```
# LLM API配置
API_URL=你的API地址
REFRESH_TOKEN=你的API密钥
MODEL_NAME=模型名称

# 新闻API配置
NEWS_API_KEY=你的NewsAPI密钥

# 邮件配置
SMTP_SERVER=SMTP服务器地址
SMTP_PORT=SMTP端口
SENDER_EMAIL=发件人邮箱
EMAIL_PASSWORD=邮箱密码
RECIPIENT_EMAIL=收件人邮箱

# 定时配置
SCHEDULE_TIME=07:00
```

## 使用方法

直接运行main.py文件启动系统：

```bash
python main.py
```

系统会立即运行一次新闻聚合流程，并根据配置的时间每天定时运行。

## 自定义

- 修改agents/integration_agent.py中的`inspirational_quotes`列表可以自定义励志名言
- 修改各个agents中的`keywords`可以调整新闻搜索关键词
- 通过修改main.py中的定时任务逻辑可以调整运行频率

## 依赖项

- Python 3.8+
- requests
- beautifulsoup4
- langchain
- langchain_openai
- python-dotenv
- schedule