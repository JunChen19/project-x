#!/usr/bin/env python3
"""
使用 Selenium 抓取文章 - 过滤广告，提取纯净内容
"""

import json
import sys
import os
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# 导入翻译模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_and_translate import translate_article

def setup_driver():
    """配置 Chrome 驱动（无头模式，自动管理驱动版本）"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36')
    
    # 屏蔽图片、CSS 等加速加载
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            'stylesheet': 2
        }
    }
    chrome_options.add_experimental_option('prefs', prefs)
    
    # 使用 webdriver-manager 自动下载匹配的 ChromeDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def extract_article_content(driver, url):
    """提取文章纯净内容，过滤广告"""
    
    print(f"  正在加载页面...")
    driver.get(url)
    
    try:
        # 等待更长时间，适应不同网站
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        # 额外等待让动态内容加载
        time.sleep(3)
    except TimeoutException:
        print("  ⚠️ 页面加载超时")
        return None
    
    # 执行 JavaScript 提取纯净内容
    script = """
    function extractCleanContent() {
        // 要移除的元素选择器（广告、导航、页脚等）
        const removeSelectors = [
            'nav', 'header:not(article header)', 'footer',
            '.advertisement', '.ads', '.ad-container', '.ad-wrapper',
            '.sidebar', '.related-posts', '.recommended', '.read-more',
            '.newsletter', '.subscribe', '.subscription', '.social-share',
            '.comments', '.comment-section', '.disqus',
            '[class*="ad-"]', '[id*="ad-"]',
            '[class*="advertisement"]', '[id*="advertisement"]',
            '[class*="promo"]', '[class*="sponsored"]',
            '.share-buttons', '.print-options', '.email-signup'
        ];
        
        // 移除不需要的元素
        removeSelectors.forEach(selector => {
            try {
                document.querySelectorAll(selector).forEach(el => el.remove());
            } catch(e) {}
        });
        
        // 查找文章容器 - 更全面的匹配
        let article = document.querySelector('article') || 
                      document.querySelector('.article-content') ||
                      document.querySelector('.post-content') ||
                      document.querySelector('.entry-content') ||
                      document.querySelector('[role="main"]') ||
                      document.querySelector('.content') ||
                      document.querySelector('.article-body') ||
                      document.querySelector('.story-content') ||
                      document.querySelector('[itemprop="articleBody"]');
        
        if (!article) {
            // 如果找不到，尝试找包含最多段落的容器
            const containers = document.querySelectorAll('div');
            let maxParagraphs = 0;
            containers.forEach(div => {
                const pCount = div.querySelectorAll('p').length;
                if (pCount > maxParagraphs && pCount > 2) {
                    maxParagraphs = pCount;
                    article = div;
                }
            });
        }
        
        if (!article) {
            article = document.body;
        }
        
        // 提取标题
        let title = document.querySelector('h1')?.textContent?.trim() || 
                    document.querySelector('title')?.textContent?.trim() || '';
        
        // 清理标题（移除网站后缀等）
        title = title.split('|')[0].split('-')[0].trim();
        
        // 提取正文段落
        let paragraphs = [];
        const contentEl = article.querySelectorAll('p, h2, h3, h4');
        contentEl.forEach(elem => {
            let text = elem.textContent.trim();
            // 过滤短文本和广告文本
            if (text.length > 80 && 
                !text.toLowerCase().includes('subscribe') &&
                !text.toLowerCase().includes('advertisement') &&
                !text.toLowerCase().includes('sponsor') &&
                !text.toLowerCase().includes('cookie') &&
                !text.toLowerCase().includes('privacy policy') &&
                !text.toLowerCase().includes('sign up') &&
                !text.toLowerCase().includes('newsletter')) {
                paragraphs.push(text);
            }
        });
        
        // 提取作者和日期
        let author = document.querySelector('[class*="author"]')?.textContent?.trim() || 
                     document.querySelector('[rel="author"]')?.textContent?.trim() || '';
        let date = document.querySelector('time')?.getAttribute('datetime') || 
                   document.querySelector('time')?.getAttribute('content') ||
                   document.querySelector('[class*="date"]')?.textContent?.trim() || '';
        
        return {
            title: title,
            paragraphs: paragraphs,
            author: author,
            date: date,
            fullText: paragraphs.join('\\n\\n')
        };
    }
    return JSON.stringify(extractCleanContent());
    """
    
    result = driver.execute_script(script)
    return json.loads(result)

def update_article(article):
    """更新单篇文章"""
    url = article['url']
    print(f"\n处理：{article['title'][:50]}...")
    print(f"URL: {url}")
    
    driver = None
    try:
        driver = setup_driver()
        content = extract_article_content(driver, url)
        
        if not content or not content['paragraphs']:
            print("  ⚠️ 无法提取内容")
            return False
        
        print(f"  ✅ 提取到 {len(content['paragraphs'])} 段")
        
        # 构建原文格式
        original = {
            'title': content['title'],
            'url': url,
            'full_text': content['fullText'],
            'content': content['paragraphs'],
            'author': content['author'],
            'published_date': content['date']
        }
        
        # 翻译
        print("  正在翻译...")
        translated = translate_article(original)
        
        # 更新文章数据
        article['full_content'] = translated['full_text']
        article['content_paragraphs'] = translated['content']
        article['original_title'] = original['title']
        article['original_content'] = original['full_text']
        article['author'] = original.get('author', '')
        
        if translated.get('image'):
            article['image'] = translated['image']
        
        print(f"  ✅ 完成")
        return True
        
    except Exception as e:
        print(f"  ❌ 错误：{e}")
        return False
    finally:
        if driver:
            driver.quit()

def load_news():
    with open('data/news.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_news(news):
    with open('data/news.json', 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=2)

def main():
    print("=" * 60)
    print("🌐 Selenium 批量抓取 AI 要闻")
    print("=" * 60)
    
    news = load_news()
    ai_articles = news['categories']['ai']
    
    # 只处理还没有完整内容的文章
    articles_to_update = [
        art for art in ai_articles 
        if 'full_content' not in art or not art.get('content_paragraphs')
    ]
    
    if not articles_to_update:
        print("✅ 所有文章已是最新！")
        return
    
    print(f"需要更新：{len(articles_to_update)} 篇")
    
    success_count = 0
    for article in articles_to_update:
        if update_article(article):
            success_count += 1
    
    # 更新时间戳
    news['lastUpdated'] = datetime.now(
        __import__('zoneinfo').ZoneInfo('Asia/Shanghai')
    ).isoformat()
    
    save_news(news)
    
    print("\n" + "=" * 60)
    print(f"✅ 完成！成功更新 {success_count}/{len(articles_to_update)} 篇")
    print("=" * 60)

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
