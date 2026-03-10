#!/usr/bin/env python3
"""
AI Brief Daily - 新闻更新脚本
功能：抓取新闻、生成摘要、分类、更新网站数据
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import hashlib

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
ARCHIVES_DIR = PROJECT_DIR / "archives"

# 模拟新闻数据（实际使用时替换为真实API）
SAMPLE_NEWS = {
    "ai": [
        {
            "title": "OpenAI 发布 GPT-5.4 多模态模型",
            "summary": "OpenAI 今日宣布推出 GPT-5.4 系列模型，包括标准版、Thinking 版和 Pro 版。新模型在推理准确性和多模态理解方面取得重大突破，错误率比 GPT-5.2 降低 33%。",
            "source": "OpenAI Blog",
            "url": "https://openai.com/blog/gpt-5-4",
            "published_at": datetime.now(timezone(timedelta(hours=8))).isoformat()
        }
    ],
    "world": [],
    "finance": [],
    "llm": []
}


def generate_id(title: str, url: str) -> str:
    """生成新闻唯一ID"""
    content = f"{title}:{url}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def archive_today_news(data: dict):
    """归档今日新闻"""
    today = datetime.now().strftime('%Y-%m-%d')
    archive_file = ARCHIVES_DIR / f"{today}.json"
    ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"已归档今日新闻到 {archive_file}")


def update_news():
    """主更新函数"""
    print(f"=== AI Brief Daily 新闻更新 ===")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 收集新闻
    all_news = {"ai": [], "world": [], "finance": [], "llm": []}
    for category, news_list in SAMPLE_NEWS.items():
        for news in news_list:
            news['id'] = generate_id(news['title'], news['url'])
            all_news[category].append(news)
    
    # 选择头条
    hero = None
    if all_news['ai']:
        hero = all_news['ai'][0]
    
    # 更新数据
    data = {
        "lastUpdated": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "hero": hero,
        "categories": {
            "ai": all_news['ai'][:5],
            "world": all_news['world'][:5],
            "finance": all_news['finance'][:5],
            "llm": all_news['llm'][:5]
        }
    }
    
    news_file = DATA_DIR / "news.json"
    with open(news_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 新闻更新完成!")
    print(f"   - 头条: {hero['title'] if hero else '无'}")
    for cat, items in data['categories'].items():
        print(f"   - {cat}: {len(items)} 条")
    
    return data


if __name__ == "__main__":
    update_news()