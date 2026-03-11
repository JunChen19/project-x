#!/usr/bin/env python3
"""
Fetch full article content from URL
"""

import requests
from bs4 import BeautifulSoup
import json
import sys

def fetch_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 获取标题
    title_tag = soup.find('h1') or soup.find('title')
    title = title_tag.get_text().strip() if title_tag else 'Unknown Title'
    
    # 获取主图
    og_image = soup.find('meta', property='og:image')
    image = og_image.get('content') if og_image else None
    
    # 获取作者
    author = None
    author_tag = soup.find('meta', attrs={'name': 'author'})
    if author_tag:
        author = author_tag.get('content')
    
    # 获取发布时间
    published_time = None
    time_tag = soup.find('meta', property='article:published_time')
    if time_tag:
        published_time = time_tag.get('content')
    
    # 获取文章内容 - TechCrunch 特定
    article_content = []
    
    # TechCrunch: article-content 或 post-content
    content_div = soup.find('div', class_='article-content')
    if not content_div:
        content_div = soup.find('div', class_='post-content')
    if not content_div:
        content_div = soup.find('article')
    
    if content_div:
        # 获取所有段落
        paragraphs = content_div.find_all(['p', 'h2', 'h3', 'ul', 'ol'])
        for elem in paragraphs:
            if elem.name == 'p':
                text = elem.get_text().strip()
                if text and len(text) > 20:
                    article_content.append({'type': 'paragraph', 'content': text})
            elif elem.name in ['h2', 'h3']:
                text = elem.get_text().strip()
                if text:
                    article_content.append({'type': 'heading', 'content': text})
            elif elem.name == 'ul':
                items = [li.get_text().strip() for li in elem.find_all('li') if li.get_text().strip()]
                if items:
                    article_content.append({'type': 'list', 'items': items})
    
    # 如果没有找到内容，尝试读取模式
    if not article_content:
        # 尝试找到所有有意义的段落
        main = soup.find('main')
        if main:
            paragraphs = main.find_all('p')
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 50:
                    article_content.append({'type': 'paragraph', 'content': text})
    
    result = {
        'title': title,
        'url': url,
        'image': image,
        'author': author,
        'published_time': published_time,
        'content': article_content,
        'full_text': '\n\n'.join([item['content'] if item['type'] == 'paragraph' else f"## {item['content']}" if item['type'] == 'heading' else '\n'.join(['- ' + i for i in item['items']]) for item in article_content])
    }
    
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fetch_article.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = fetch_article(url)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
