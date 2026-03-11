#!/usr/bin/env python3
"""
AI Brief Daily - 新闻更新脚本
功能：读取 news.json 数据，更新网站
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


def generate_id(title: str, url: str) -> str:
    """生成新闻唯一 ID"""
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
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 读取已更新的 news.json 数据
    news_file = DATA_DIR / "news.json"
    if not news_file.exists():
        print("❌ news.json 不存在，请先运行数据更新脚本")
        return None
    
    with open(news_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 检查是否是新的数据格式
    if 'categories' in raw_data and isinstance(raw_data['categories'], dict):
        # 新格式：包含 ai_news, international_news, finance_news, llm_news
        categories_map = {
            'ai_news': 'ai',
            'international_news': 'world',
            'finance_news': 'finance',
            'llm_news': 'llm'
        }
        
        all_news = {"ai": [], "world": [], "finance": [], "llm": []}
        
        for source_key, target_key in categories_map.items():
            if source_key in raw_data['categories']:
                for item in raw_data['categories'][source_key]['items']:
                    news_item = {
                        'title': item['title'],
                        'summary': item['summary'],
                        'source': item.get('source', 'News Source'),
                        'url': item['url'],
                        'published_at': item.get('date', datetime.now().isoformat()),
                        'id': generate_id(item['title'], item['url']),
                        'image': item.get('image')
                    }
                    all_news[target_key].append(news_item)
        
        # 选择头条（优先大模型新闻，其次 AI 新闻）
        hero = None
        if all_news['llm']:
            hero = all_news['llm'][0]
        elif all_news['ai']:
            hero = all_news['ai'][0]
        
        # 更新数据
        data = {
            "lastUpdated": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "hero": hero,
            "categories": {
                "ai": all_news['ai'][:6],
                "world": all_news['world'][:6],
                "finance": all_news['finance'][:6],
                "llm": all_news['llm'][:6]
            }
        }
        
        # 写回 news.json
        with open(news_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 新闻更新完成!")
        print(f"   - 头条：{hero['title'] if hero else '无'}")
        for cat, items in data['categories'].items():
            print(f"   - {cat}: {len(items)} 条")
        
        return data
    else:
        # 旧格式，直接使用
        print(f"✅ 新闻更新完成!")
        print(f"   - 头条：{raw_data.get('hero', {}).get('title', '无')}")
        for cat, items in raw_data.get('categories', {}).items():
            print(f"   - {cat}: {len(items)} 条")
        return raw_data


if __name__ == "__main__":
    update_news()
