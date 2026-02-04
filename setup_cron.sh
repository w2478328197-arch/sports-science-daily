#!/bin/bash

# Get absolute path of current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="$DIR/daily_sports_update.py"

# Load environment variables if .env exists
if [ -f "$DIR/.env" ]; then
    export $(grep -v '^#' "$DIR/.env" | xargs)
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3。请确保已安装 Python 3。"
    exit 1
fi

# The command to run (Force UTF-8 for logging)
export PYTHONIOENCODING=utf-8
PYTHON_CMD="$(which python3) \"$PYTHON_SCRIPT\" --days 1 >> \"$DIR/cron.log\" 2>&1"

# 9:00 AM every day
CRON_JOB="0 9 * * * cd \"$DIR\" && $PYTHON_CMD"

# Check if job already exists
(crontab -l 2>/dev/null | grep -F "$PYTHON_SCRIPT") && echo "⚠️ 任务已存在于 crontab 中。" && exit 0

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ 定时任务成功设置！"
echo "📅 任务计划: 每天上午 9:00 执行"
echo "📜 脚本路径: $PYTHON_SCRIPT"
echo "📝 日志文件: $DIR/cron.log"
echo ""
echo "💡 提示: 如果需要自动同步到 Notion，请在同目录下创建 .env 文件并填入:"
echo "NOTION_TOKEN=your_token"
echo "NOTION_PAGE_ID=your_page_id"
