# 🏃‍♂️ Sports Science Daily / 运动科学日报自动更新系统

**Automated Daily Sports Science & Wearable Tech Reports**  
**自动化的运动科学与可穿戴科技日报生成系统**

This project automatically fetches, filters, translates, and summarizes the latest sports science research (PubMed) and industry news (RSS Feeds) into a clean daily report, synced directly to your Notion workspace.
本项目自动抓取、筛选、翻译并总结最新的运动科学研究（PubMed）和行业新闻（RSS 源），生成干净的日报并同步到您的 Notion 工作区。

---

## ✨ Features / 功能亮点

-   **🔍 Dual-Source Intelligence**: Fetches peer-reviewed papers from PubMed and latest tech news from industry blogs.
    **双源情报**: 同时抓取 PubMed 同行评审论文和行业博客的最新科技新闻。
-   **🧠 Smart Deduplication**: Intelligent history tracking prevents duplicate content in your daily reports.
    **智能去重**: 内置历史追踪机制，确保日报中不会出现重复内容。
-   **📝 AI Translation & Summarization**: Automatically translates abstracts and summaries into Chinese.
    **AI 翻译与总结**: 自动将英文摘要和新闻概要翻译成中文。
-   **🔄 Notion Integration**: One-click sync to your Notion database or page.
    **Notion 集成**: 一键同步生成的内容到您的 Notion 数据库或页面。
-   **🤖 Agent Skill Ready**: Includes configuration to be used as an AI Agent Skill.
    **AI Agent 就绪**: 包含作为 AI Agent Skill 使用的配置文件。

---

## 🛠 Prerequisites / 准备工作

-   Python 3.8+
-   Notion Integration Token (Internal Integration)

---

## 🚀 Installation / 安装

1.  **Clone the repository / 克隆仓库**
    ```bash
    git clone https://github.com/w2478328197-arch/sports-science-daily.git
    cd sports-science-daily
    ```

2.  **Install dependencies / 安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration / 配置**
    Create a `.env` file in the root directory:
    在根目录创建一个 `.env` 文件：

    ```env
    # .env
    NOTION_TOKEN=your_integration_token_here
    NOTION_PAGE_ID=your_page_id_here
    ```

---

## 📖 Usage / 使用方法

### Basic Run / 基础运行
Generate the daily report for the last 2 days (default):
生成过去 2 天（默认）的日报：

```bash
python daily_sports_update.py
```

### Advanced Options / 高级选项

-   **Lookback Period / 回溯时间**:
    Fetch content from the last 7 days:
    抓取过去 7 天的内容：
    ```bash
    python daily_sports_update.py --days 7
    ```

-   **Force Refresh / 强制刷新**:
    Ignore history and fetch everything (useful for debugging):
    忽略历史记录，强制抓取所有内容（调试用）：
    ```bash
    python daily_sports_update.py --no-history
    ```

---

## 📂 Project Structure / 项目结构

*   `daily_sports_update.py`: Main crawler & generator script. (核心爬虫与生成脚本)
*   `processed_history.json`: Stores processed links to prevent duplicates. (存储已处理链接以去重)
*   `.agent/skills/`: Configuration for AI Agent integration. (AI Agent 集成配置)
*   `requirements.txt`: Python dependencies. (Python 依赖)

---

## 🤝 Contributing / 贡献

Contributions are welcome! Please feel free to verify the `processed_history.json` is in `.gitignore` before submitting a Pull Request.
欢迎提交 PR！提交前请确保 `.gitignore` 中包含了 `processed_history.json` 以保护您的本地历史记录。

---

## 📜 License

MIT License
