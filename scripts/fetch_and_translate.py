#!/usr/bin/env python3
"""
Fetch full article content from URL and translate to Chinese
"""

import requests
from bs4 import BeautifulSoup
import json
import sys
import time

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
    
    # 获取文章内容
    article_content = []
    
    # TechCrunch 使用 entry-content
    content_div = soup.find('div', class_='entry-content')
    if not content_div:
        content_div = soup.find('div', class_='article-content')
    if not content_div:
        content_div = soup.find('div', class_='post-content')
    if not content_div:
        content_div = soup.find('article')
    
    if content_div:
        paragraphs = content_div.find_all(['p', 'h2', 'h3'])
        for elem in paragraphs:
            if elem.name in ['p', 'h2', 'h3']:
                text = elem.get_text().strip()
                # 过滤广告和推广内容
                if text and len(text) > 50:
                    # 跳过包含注册、购票等广告词的段落
                    skip_keywords = ['REGISTER NOW', 'Register Now', 'ticket savings', 'Ends 11:59', 'save up to']
                    if any(keyword in text for keyword in skip_keywords):
                        continue
                    article_content.append(text)
    
    result = {
        'title': title,
        'url': url,
        'image': image,
        'author': author,
        'published_time': published_time,
        'content': article_content,
        'full_text': '\n\n'.join(article_content)
    }
    
    return result

def translate_text(text, source='en', target='zh-CN'):
    """使用 MyMemory 免费翻译 API"""
    try:
        url = f'https://api.mymemory.translated.net/get?q={requests.utils.quote(text)}&langpair={source}|{target}'
        response = requests.get(url, timeout=10)
        result = response.json()
        translated = result.get('responseData', {}).get('translatedText', text)
        time.sleep(0.5)  # 避免速率限制
        return translated
    except Exception as e:
        print(f"翻译失败：{e}")
        return text

def translate_article(article):
    """翻译整篇文章"""
    print(f"  翻译标题...")
    translated_title = translate_text(article['title'])
    
    print(f"  翻译正文 ({len(article['content'])} 段)...")
    translated_content = []
    for i, para in enumerate(article['content'], 1):
        print(f"    {i}/{len(article['content'])}", end='\r')
        translated_content.append(translate_text(para))
    print()
    
    translated = {
        'title': translated_title,
        'url': article.get('url', ''),
        'image': article.get('image'),
        'author': article.get('author', ''),
        'published_time': article.get('published_time', ''),
        'content': translated_content,
        'full_text': '\n\n'.join(translated_content)
    }
    return translated

def generate_html(article, translated, output_file):
    """生成 HTML 预览页面"""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{translated['title']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f5f5f5;
        }}
        .article {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .article img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .article h1 {{
            font-size: 28px;
            margin-bottom: 15px;
            color: #1a1a1a;
        }}
        .meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        .article p {{
            margin-bottom: 20px;
            color: #333;
            font-size: 16px;
        }}
        .source-link {{
            display: inline-block;
            margin-top: 30px;
            padding: 10px 20px;
            background: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        }}
        .source-link:hover {{
            background: #0055aa;
        }}
        .original-toggle {{
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <article class="article">
        <h1>{translated['title']}</h1>
        <div class="meta">
            <span>作者：{translated['author'] or '未知'}</span> | 
            <span>时间：{translated['published_time'] or '未知'}</span> |
            <span>来源：TechCrunch</span>
        </div>
        <img src="{translated['image'] or ''}" alt="Article Image" onerror="this.style.display='none'">
'''
    
    for para in translated['content']:
        html += f'        <p>{para}</p>\n'
    
    html += f'''
        <div class="original-toggle">
            <strong>📄 原文标题：</strong>{article['title']}<br><br>
            <a href="{article['url']}" class="source-link" target="_blank">查看原文 →</a>
        </div>
    </article>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fetch_and_translate.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print("=" * 60)
    print("📰 文章抓取 + 翻译工具")
    print("=" * 60)
    
    print("\n[1/3] 正在抓取原文...")
    article = fetch_article(url)
    
    print(f"✅ 标题：{article['title'][:60]}...")
    print(f"✅ 图片：{'有' if article['image'] else '无'}")
    print(f"✅ 段落：{len(article['content'])} 段")
    
    print("\n[2/3] 正在翻译...")
    translated = translate_article(article)
    
    print(f"✅ 翻译完成")
    
    print("\n[3/3] 生成预览页面...")
    generate_html(article, translated, 'translated_article.html')
    print(f"✅ 预览页面：translated_article.html")
    
    # 保存 JSON
    with open('translated_article.json', 'w', encoding='utf-8') as f:
        json.dump({
            'original': article,
            'translated': translated
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON 数据：translated_article.json")
    
    print("\n" + "=" * 60)
    print("🎉 完成！预览：")
    print("=" * 60)
    print(f"\n标题：{translated['title']}")
    print(f"\n前 3 段预览：")
    for i, para in enumerate(translated['content'][:3], 1):
        print(f"{i}. {para[:100]}...")
    
    print(f"\n💡 打开预览：open translated_article.html")
