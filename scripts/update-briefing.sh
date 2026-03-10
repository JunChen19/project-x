#!/bin/bash
# AI Brief Daily - 更新脚本入口
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始更新 AI Brief Daily" | tee -a "$LOG_DIR/update.log"
cd "$PROJECT_DIR"
python3 "$SCRIPT_DIR/update_news.py" | tee -a "$LOG_DIR/update.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 更新完成" | tee -a "$LOG_DIR/update.log"