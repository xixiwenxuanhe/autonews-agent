# NewsMailAgent 📰✉️

## 功能概述 🌟

- 🔍 自动收集技术、经济和生物学领域的最新新闻
- 🌐 支持中英文双语新闻搜索与处理
- 🧠 基于LLM的文章筛选与内容相关性评估
- 📊 自动整合多领域新闻内容，生成结构化简报
- 📧 邮件自动分发系统，支持多收件人
- ⏰ 支持定时调度执行

## 环境配置 🛠️

### 依赖安装 📦

```bash
pip install -r requirements.txt
```

### 环境变量配置 ⚙️

复制环境变量模板文件：

```bash
cp .env.example .env
```

配置`.env`文件内容：

```
# API配置
NEWS_API_KEY=your_news_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 邮件服务配置
EMAIL_SENDER=your_email@example.com
EMAIL_PASSWORD=your_email_password
EMAIL_RECEIVER=recipient1@example.com,recipient2@example.com,2563374153@qq.com
SMTP_SERVER=smtp.example.com
SMTP_PORT=587

# 调度配置
SCHEDULE_TIME=07:00
```

配置说明：
- 🔑 `NEWS_API_KEY`: NewsAPI接口密钥
- 🔑 `OPENAI_API_KEY`: OpenAI API密钥，用于内容生成与筛选
- 📨 `EMAIL_SENDER`: 发送邮箱地址
- 🔒 `EMAIL_PASSWORD`: 发送邮箱密码或应用专用密码
- 📩 `EMAIL_RECEIVER`: 接收邮箱地址，多个地址用逗号分隔
- 🖥️ `SMTP_SERVER`: SMTP服务器地址
- 🔌 `SMTP_PORT`: SMTP服务器端口
- 🕗 `SCHEDULE_TIME`: 定时执行时间(HH:MM格式)

## 使用方法 📋

### 标准模式 🚀

```bash
python main.py
```

启动完整的新闻聚合流程，包括LLM关键词生成、新闻检索、内容整合及邮件分发。

### 预设关键词模式 🔍

```bash
python main.py --hard=true
```

使用系统预设的关键词组合进行搜索，输出详细的检索结果，便于调试和验证。此模式仍执行完整的内容整合和邮件分发流程。

### 邮件测试模式 📧

```bash
python main.py --sent=false
```

仅执行新闻收集和内容整合流程，但不发送邮件，适用于开发和测试阶段。

参数说明：
- 🔄 `--hard=true`: 启用预设关键词组合并输出详细检索结果
- 📧 `--sent=false`: 禁用邮件发送功能，仅执行新闻收集和内容整合

## 项目结构 📁

```
/
├── agents/                # 智能代理模块
│   ├── base_agent.py     # 基础代理类
│   ├── search_agent.py   # 搜索代理
│   ├── integration_agent.py # 内容整合代理
│   ├── email_agent.py    # 邮件分发代理
│   └── keywords.json     # 关键词数据库
├── main.py               # 程序入口
├── .env.example          # 环境变量模板
├── .env                  # 环境变量配置（需自行创建）
└── requirements.txt      # 项目依赖
```

## 高级配置 🔧

### 关键词定制 🔤

通过修改`agents/keywords.json`文件可自定义各领域的预设关键词库，系统将基于此生成搜索查询组合。

### 领域提示词配置 🎯

`search_agent.py`中的`domain_prompts`字典定义了各领域的文章筛选标准，可根据需求调整筛选参数和权重。

## LLM集成技术 🧠

系统在多个关键环节利用大语言模型(LLM)技术：

### 关键词生成系统 🔍
- 为技术、经济及生物学领域动态生成关键词组合
- 并行生成中英文关键词，确保语言间的关键词差异化
- 优化关键词分布，最大化信息覆盖面

### 内容筛选引擎 📊
- 基于领域特定筛选标准评估文章相关性和重要性
- 自动筛选高价值文章，降低信息冗余
- 确保筛选结果在领域内保持多样性和代表性

### 邮件标题生成机制 📝
- 基于文章集合生成描述性邮件标题
- 提取关键信息点，形成结构化标题

### 跨领域内容管理 🔄
- 基于URL和标题的文章去重系统
- 在保持信息完整性的同时优化阅读体验
- 多语言内容的平衡处理与组织

## 故障排查 ❓

API密钥错误：
- 检查`.env`文件配置及环境变量加载状态

搜索结果质量问题：
- 使用`--hard=true`参数运行进行结果验证
- 审查并优化`keywords.json`中的关键词配置
- 调整`search_agent.py`中的领域筛选参数

## 许可证 📄

[MIT License](LICENSE)
