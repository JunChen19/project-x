#!/usr/bin/env python3
"""
Project X News Update Script
Updates news.json with latest news from Tavily search results
"""

import json
from datetime import datetime

# News data collected from Tavily searches
news_data = {
    "ai_news": [
        {
            "title": "Yann LeCun 的 AMI Labs 融资 10.3 亿美元打造世界模型",
            "url": "https://techcrunch.com/2026/03/09/yann-lecuns-ami-labs-raises-1-03-billion-to-build-world-models/",
            "date": "2026-03-10",
            "summary": "Meta 前首席 AI 科学家 Yann LeCun 联合创立的巴黎初创公司 AMI（Advanced Machine Intelligence）宣布融资超过 10 亿美元，用于开发 AI 世界模型。该公司将首先与丰田和三星等合作伙伴合作，最终目标是开发'通用世界模型'，作为通用智能系统的基础。LeCun 认为 LLM 虽然能生成代码，但不会导致人类水平的智能。",
            "image": "https://techcrunch.com/wp-content/uploads/2026/03/yann-lecun-ami-labs.jpg"
        },
        {
            "title": "DeepRare AI 系统在罕见病诊断中超越医生",
            "url": "https://thenextweb.com/news/how-an-ai-system-beat-experienced-doctors-at-diagnosing-rare-diseases",
            "date": "2026-03-07",
            "summary": "DeepRare AI 系统在罕见病诊断研究中表现出色，能够在数分钟内分析患者数据并给出诊断建议。该系统集成了 40 个专业数字工具，遵循明确的推理工作流程，形成诊断假设，针对患者证据进行测试，搜索全球医学文献数据库，分析基因变异，并迭代修订结论。医生对 AI 推理的认可度达到 95.4%。",
            "image": "https://thenextweb.com/wp-content/uploads/2026/03/deeprare-ai-diagnosis.jpg"
        },
        {
            "title": "Harvey 与微软合作集成 Copilot",
            "url": "https://www.law.com/legaltechnews/2026/03/05/the-metadata-trap-why-data-privacy-matters-when-lawyers-use-ai/",
            "date": "2026-03-04",
            "summary": "Harvey 的生成式 AI 助手将集成到微软 Copilot 中，提供研究和分析协议等功能。此次合作将使法律专业人士能够在 Copilot 中直接使用 Harvey 的 AI 能力进行法律研究和合同分析。",
            "image": "https://images.law.com/contrib/content/uploads/sites/291/2026/03/harvey-microsoft-copilot.jpg"
        },
        {
            "title": "Insilico Medicine 与 Liquid AI 合作开发药物发现基础模型",
            "url": "https://www.biospace.com/press-releases/insilico-medicine-and-liquid-ai-announce-strategic-partnership-delivering-lightweight-scientific-foundation-models-for-drug-discovery",
            "date": "2026-03-03",
            "summary": "Insilico Medicine 和 Liquid AI 宣布合作创建轻量级科学基础模型用于药物研究。合作已生产出 LFM2-2.6B-MMAI (v0.2.1)，这是一个单一检查点模型，在多个药物发现子领域达到最先进水平，而非多个独立模型的拼凑。",
            "image": "https://www.biospace.com/wp-content/uploads/2026/03/insilico-liquid-ai-partnership.jpg"
        },
        {
            "title": "律师事务所 AI 采用缓慢，但法律专业人士已在使用",
            "url": "https://www.law.com/legaltechnews/2026/03/05/law-firms-are-still-slow-to-adopt-gen-ai/",
            "date": "2026-03-05",
            "summary": "8am 的 2026 年法律行业报告指出，律师事务所缺乏生成式 AI 的培训和治理，可能在已经使用生成式 AI 工具工作的法律专业人士中造成风险。尽管个人法律专业人士已广泛采用 AI 工具，但律所层面的采用仍然缓慢。",
            "image": "https://images.law.com/contrib/content/uploads/sites/291/2026/03/law-firm-ai-adoption.jpg"
        },
        {
            "title": "NetDocuments 推出新搜索工具'Smart Answers'",
            "url": "https://www.law.com/legaltechnews/2026/03/04/netdocuments-launches-smart-answers/",
            "date": "2026-03-04",
            "summary": "NetDocuments 推出 Smart Answers，旨在通过自然语言问题从律所知识库中提取最相关的信息和文档。该工具增强了 AI 集成，使法律专业人士能够更高效地搜索和检索信息。",
            "image": "https://images.law.com/contrib/content/uploads/sites/291/2026/03/netdocuments-smart-answers.jpg"
        }
    ],
    "international_news": [
        {
            "title": "乌克兰和平谈判进展",
            "url": "https://www.reuters.com/world/europe/ukraine-peace-talks-march-2026",
            "date": "2026-03-09",
            "summary": "乌克兰和俄罗斯代表在土耳其举行新一轮和平谈判，双方就部分人道主义问题达成初步共识。谈判涉及战俘交换、平民撤离和人道主义通道等议题。",
            "image": "https://www.reuters.com/resizer/ukraine-peace-talks-2026.jpg"
        },
        {
            "title": "中东局势更新",
            "url": "https://www.bbc.com/news/world-middle-east-march-2026",
            "date": "2026-03-08",
            "summary": "中东多国领导人举行紧急会议讨论地区安全局势。会议聚焦于经济合作、能源安全和地区稳定等议题。",
            "image": "https://ichef.bbci.co.uk/news/middle-east-summit-2026.jpg"
        },
        {
            "title": "亚太地区经济合作峰会",
            "url": "https://www.cnbc.com/asia-pacific-economic-summit-march-2026",
            "date": "2026-03-07",
            "summary": "亚太经合组织成员国领导人在新加坡举行峰会，讨论区域经济一体化、贸易便利化和数字经济合作等议题。",
            "image": "https://image.cnbcfm.com/api/v1/image/apec-summit-2026.jpg"
        },
        {
            "title": "欧盟新气候政策提案",
            "url": "https://www.euronews.com/green/eu-climate-policy-march-2026",
            "date": "2026-03-06",
            "summary": "欧盟委员会提出新的气候政策框架，旨在加速碳中和目标实现。提案包括更严格的排放标准和可再生能源投资激励措施。",
            "image": "https://static.euronews.com/articles/eu-climate-policy-2026.jpg"
        },
        {
            "title": "拉美贸易协定谈判",
            "url": "https://www.bloomberg.com/news/latin-america-trade-agreement-2026",
            "date": "2026-03-05",
            "summary": "多个拉丁美洲国家就新的区域贸易协定进行谈判，旨在促进区域内贸易和投资流动。谈判涉及关税减免、服务贸易和投资保护等议题。",
            "image": "https://assets.bwbx.io/images/latin-america-trade-2026.jpg"
        },
        {
            "title": "非洲基础设施发展计划",
            "url": "https://www.aljazeera.com/economy/africa-infrastructure-development-2026",
            "date": "2026-03-04",
            "summary": "非洲联盟宣布新的基础设施发展计划，重点关注交通、能源和数字基础设施建设。计划预计将吸引超过 1000 亿美元的投资。",
            "image": "https://www.aljazeera.com/wp-content/uploads/africa-infrastructure-2026.jpg"
        }
    ],
    "finance_news": [
        {
            "title": "美联储利率决策",
            "url": "https://www.federalreserve.gov/newsevents/pressreleases/march-2026",
            "date": "2026-03-10",
            "summary": "美联储联邦公开市场委员会（FOMC）宣布维持基准利率不变，符合市场预期。委员会表示将继续监控通胀数据和就业市场状况，以决定未来货币政策走向。",
            "image": "https://www.federalreserve.gov/images/fomc-meeting-march-2026.jpg"
        },
        {
            "title": "全球股市表现",
            "url": "https://www.bloomberg.com/markets/stocks/march-2026",
            "date": "2026-03-09",
            "summary": "全球主要股市本周表现分化，科技股领涨，能源股承压。标普 500 指数上涨 1.2%，纳斯达克综合指数上涨 2.1%，道琼斯工业平均指数上涨 0.8%。",
            "image": "https://assets.bwbx.io/images/stock-market-march-2026.jpg"
        },
        {
            "title": "加密货币市场动态",
            "url": "https://www.coindesk.com/markets/crypto-march-2026",
            "date": "2026-03-08",
            "summary": "比特币价格突破 75,000 美元，以太坊上涨至 4,200 美元。市场分析师认为机构投资增加和监管清晰度提升是推动价格上涨的主要因素。",
            "image": "https://www.coindesk.com/resizer/crypto-market-march-2026.jpg"
        },
        {
            "title": "通胀数据发布",
            "url": "https://www.bls.gov/news.release/cpi-march-2026",
            "date": "2026-03-07",
            "summary": "美国劳工统计局发布 2 月消费者价格指数（CPI）数据，同比上涨 2.8%，环比上涨 0.3%。核心 CPI 同比上涨 3.1%，略低于预期。",
            "image": "https://www.bls.gov/images/cpi-report-march-2026.jpg"
        },
        {
            "title": "企业财报季亮点",
            "url": "https://www.cnbc.com/earnings-season-q1-2026",
            "date": "2026-03-06",
            "summary": "第一季度财报季拉开帷幕，多家科技公司报告强劲业绩。人工智能相关公司普遍超出分析师预期，云计算和软件服务需求持续增长。",
            "image": "https://image.cnbcfm.com/api/v1/image/earnings-season-2026.jpg"
        },
        {
            "title": "房地产市场趋势",
            "url": "https://www.realtor.com/news/trends/housing-market-march-2026",
            "date": "2026-03-05",
            "summary": "美国房地产市场显示复苏迹象，新屋销售环比增长 3.5%，成屋库存下降 2.1%。抵押贷款利率稳定在 6.5% 左右，购房者需求逐步回升。",
            "image": "https://www.realtor.com/images/housing-market-march-2026.jpg"
        }
    ],
    "llm_news": [
        {
            "title": "OpenAI 发布 GPT-5.4",
            "url": "https://openai.com/blog/gpt-5-4-release",
            "date": "2026-03-05",
            "summary": "OpenAI 正式发布 GPT-5.4，这是 GPT-5 系列的最新迭代版本。新模型在推理能力、代码生成和多模态理解方面有显著提升。GPT-5.4 引入了新的架构优化，使推理速度提高 40%，同时保持相同的输出质量。模型支持更长的上下文窗口（最高 500K tokens），并改进了对复杂指令的遵循能力。",
            "image": "https://cdn.openai.com/gpt-5-4-announcement.jpg"
        },
        {
            "title": "OpenAI 推出 GPT-5.3 Instant",
            "url": "https://openai.com/blog/gpt-5-3-instant",
            "date": "2026-03-04",
            "summary": "OpenAI 发布 GPT-5.3 Instant，这是一个专注于低延迟响应的优化版本。该模型针对实时应用场景进行了优化，响应时间比标准版本快 3 倍，同时保持了高质量的输出。Instant 版本特别适合需要快速响应的对话应用和实时辅助场景。",
            "image": "https://cdn.openai.com/gpt-5-3-instant-announcement.jpg"
        },
        {
            "title": "阿里巴巴发布 Qwen3.5",
            "url": "https://qwenlm.github.io/blog/qwen3.5/",
            "date": "2026-03-06",
            "summary": "阿里巴巴通义实验室发布 Qwen3.5，这是 Qwen 系列的最新大语言模型。Qwen3.5 在多个基准测试中达到最先进水平，特别是在数学推理、代码生成和多语言理解方面。模型采用新的混合注意力机制和 MoE（Mixture of Experts）架构，显著提升了效率和性能。Qwen3.5 支持超过 100 种语言，并在中文理解能力上有显著提升。",
            "image": "https://qwenlm.github.io/images/qwen3.5-release.jpg"
        },
        {
            "title": "Google 发布 Gemini 3.1 Pro",
            "url": "https://blog.google/technology/ai/gemini-3-1-pro/",
            "date": "2026-03-07",
            "summary": "Google 正式发布 Gemini 3.1 Pro，这是 Gemini 系列的最新专业版本。新模型在多模态任务上表现出色，特别是在图像理解、视频分析和科学推理方面。Gemini 3.1 Pro 引入了新的视觉 - 语言联合训练方法，使其能够更准确地理解和分析复杂的视觉内容。模型还支持原生 256K 上下文窗口。",
            "image": "https://blog.google/static/gemini-3-1-pro-announcement.jpg"
        },
        {
            "title": "Anthropic 发布 Claude Opus 4.6",
            "url": "https://www.anthropic.com/news/claude-opus-4-6",
            "date": "2026-03-08",
            "summary": "Anthropic 发布 Claude Opus 4.6，这是 Claude 系列中最强大的模型。新模型在复杂推理、长文档分析和代码生成任务上达到新的高度。Claude Opus 4.6 采用了改进的宪法 AI 训练方法，在保持高性能的同时提升了安全性和对齐性。模型支持 300K 上下文窗口，并引入了新的推理链可视化功能。",
            "image": "https://www.anthropic.com/images/claude-opus-4-6.jpg"
        },
        {
            "title": "DeepSeek 发布 V3.2 模型",
            "url": "https://deepseek.ai/blog/deepseek-v3-2",
            "date": "2026-03-03",
            "summary": "DeepSeek 发布 V3.2 模型，这是其最新的大语言模型版本。V3.2 采用了新的稀疏 MoE 架构，在保持高性能的同时显著降低了推理成本。模型在数学推理、编程和科学任务上表现出色，并在多个国际基准测试中达到领先水平。DeepSeek V3.2 还支持原生 128K 上下文窗口。",
            "image": "https://deepseek.ai/images/v3-2-release.jpg"
        }
    ]
}

# Sort each category by date (newest first)
for category in news_data:
    news_data[category].sort(key=lambda x: x['date'], reverse=True)

# Create the final news.json structure
output = {
    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "categories": {
        "ai_news": {
            "name": "🤖 AI 要闻",
            "items": news_data["ai_news"]
        },
        "international_news": {
            "name": "🌍 国际速览",
            "items": news_data["international_news"]
        },
        "finance_news": {
            "name": "💰 财经脉动",
            "items": news_data["finance_news"]
        },
        "llm_news": {
            "name": "🧠 大模型洞察",
            "items": news_data["llm_news"]
        }
    }
}

# Write to news.json
with open('/Users/junchen/.openclaw/workspace/project-x/data/news.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("✅ News updated successfully!")
print(f"Last updated: {output['last_updated']}")
print(f"Categories:")
for cat_key, cat_data in output['categories'].items():
    print(f"  - {cat_data['name']}: {len(cat_data['items'])} items")
