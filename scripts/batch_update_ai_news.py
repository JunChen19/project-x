#!/usr/bin/env python3
"""
批量更新 AI 要闻文章 - 抓取原文并翻译
"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_and_translate import fetch_article, translate_article

def load_news():
    with open('data/news.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_news(news):
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)

def update_article(article, index, total):
    """更新单篇文章"""
    print(f"\n[{index}/{total}] 处理：{article['title'][:40]}...")
    
    try:
        url = article['url']
        print(f"  URL: {url}")
        
        # 抓取原文
        print("  正在抓取...")
        original = fetch_article(url)
        
        if not original['content']:
            print(f"  ⚠️ 无法抓取内容，跳过")
            return False
        
        print(f"  ✅ 抓取到 {len(original['content'])} 段")
        
        # 翻译
        print("  正在翻译...")
        translated = translate_article(original)
        
        # 更新文章数据
        article['full_content'] = translated['full_text']
        article['content_paragraphs'] = translated['content']
        article['original_title'] = original['title']
        article['original_content'] = original['full_text']
        
        if translated['image']:
            article['image'] = translated['image']
        
        print(f"  ✅ 翻译完成")
        return True
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        return False

def main():
    print("=" * 60)
    print("📰 批量更新 AI 要闻")
    print("=" * 60)
    
    news = load_news()
    ai_articles = news['categories']['ai']
    
    print(f"共 {len(ai_articles)} 篇文章需要更新")
    
    success_count = 0
    for i, article in enumerate(ai_articles, 1):
        if update_article(article, i, len(ai_articles)):
            success_count += 1
    
    # 保存更新
    news['lastUpdated'] = json.dumps(__import__('datetime').datetime.now(
        __import__('zoneinfo').ZoneInfo('Asia/Shanghai')
    ).isoformat())
    
    save_news(news)
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！成功更新 {success_count}/{len(ai_articles)} 篇")
    print(f"📄 已保存到：data/news.json")
    print("=" * 60)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
