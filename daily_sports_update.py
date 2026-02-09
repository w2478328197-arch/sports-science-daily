import feedparser
import datetime
import os
import ssl
import re
import urllib.request
import urllib.parse
import json
import argparse
import time
import xml.etree.ElementTree as ET
from datetime import timezone

def load_env_file(filepath):
    """Load .env file manually without external dependencies"""
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key_val = line.strip().split('=', 1)
                    if len(key_val) == 2:
                        env_vars[key_val[0]] = key_val[1]
    return env_vars

# Load .env variables
env_vars = load_env_file(os.path.join(os.path.dirname(__file__), '.env'))

# Notion 配置 (优先使用环境变量，其次使用 .env 文件)
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", env_vars.get("NOTION_TOKEN", ""))
NOTION_PAGE_ID = os.environ.get("NOTION_PAGE_ID", env_vars.get("NOTION_PAGE_ID", ""))

# 脚本配置
ITEMS_PER_FEED = 20         # 增加到 20 以防止像 Huawei Central 这样高频更新的源丢失数据
TRANSLATION_LIMIT = 2000   # 摘要翻译字数限制 (增加以容纳完整摘要)
RETMAX_PUBMED = 50         # PubMed 每次检索数量 (Increased from 15 to 50 for broader coverage)

# 配置 SSL (解决某些环境下的证书问题)
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# --- 1. 精选科研/专家源 (Whitelist Only) ---
# 严格筛选，按照用户的三大板块重组

# 板块 1: 我喜欢的博主的动向 (合并了原有的科研博客和专家频道)
# 板块 1: 我喜欢的博主的动向 (合并了原有的科研博客和专家频道)
# 板块 1: 我喜欢的博主的动向 (合并了原有的科研博客和专家频道)
BLOGGER_FEEDS = [
    ("Stronger by Science (Nuckols)", "https://www.strongerbyscience.com/feed/"),
    ("Mysportscience (Jeukendrup)", "https://www.mysportscience.com/blog-feed.xml"),
    ("Peter Attia (Longevity)", "https://peterattiadrive.libsyn.com/rss"),
    ("Andrew Huberman (Podcast)", "https://feeds.megaphone.fm/hubermanlab"),
    ("Science for Sport", "https://www.scienceforsport.com/feed/"), 
    ("YLMSportScience", "https://ylmsportscience.com/feed/"),
    ("Bryan Johnson (Blueprint)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCnRVL1-HJnXWB_Xi2dAoTcg"),
    ("Jeff Nippard (Science Explained)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCjTp-nBKswYLumqmVeBPwYw"),
    ("Renaissance Periodization (Dr. Mike)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCfQgsKhHjSyRLOp9mnffqVg"),
    ("Andy Galpin (Human Performance)", "https://www.youtube.com/feeds/videos.xml?channel_id=UCe3R2e3zYxWwIhMKV36Qhkw"),
    ("JB Morin (Biomechanics)", "https://jb-morin.net/feed/"),
]

# 板块 2: 智能可穿戴动向 (Fitbit/Whoop/Garmin/Apple/Oura)
INDUSTRY_FEEDS = [
    ("DC Rainmaker (Wearable Tech)", "https://www.dcrainmaker.com/feed"),
    ("Google Research (Health & Bioscience)", "https://research.google/blog/rss/"),
    ("Whoop Podcast (Recovery Science)", "https://feeds.buzzsprout.com/230442.rss"),
    ("Oura Engineering (Tech Blog)", "https://ouraring.wpengine.com/category/meet-oura/feed/"), # Ensuring we get technical posts
    ("Fitbit (Google Blog)", "https://blog.google/products/fitbit/rss/"),
    ("Garmin Blog", "https://www.garmin.com/en-US/blog/feed/"),
    ("Polar Blog", "https://www.polar.com/blog/feed/"),
    ("Oura Ring Blog", "https://ouraring.com/blog/feed/"),
    ("Apple Newsroom (Health)", "https://www.apple.com/newsroom/rss-feed.rss"),
]

RSS_FEEDS = {
    "bloggers": BLOGGER_FEEDS,
    "industry": INDUSTRY_FEEDS
}

# PubMed 顶刊列表 (扩展至 22 个全球顶尖期刊)
PUBMED_JOURNALS = [
    # 运动医学/临床类
    "British Journal of Sports Medicine",
    "The American Journal of Sports Medicine",
    "Sports Medicine",
    "Scandinavian Journal of Medicine & Science in Sports",
    "Knee Surgery, Sports Traumatology, Arthroscopy",
    "Journal of Orthopaedic & Sports Physical Therapy",
    "Sports Health",
    "Clinical Journal of Sport Medicine",
    
    # 生理学/生物化学类
    "Journal of Applied Physiology",
    "European Journal of Applied Physiology",
    "Journal of Strength and Conditioning Research",
    "Medicine and Science in Sports and Exercise",
    
    # 表现/应用科学类
    "International Journal of Sports Physiology and Performance",
    "Journal of Sports Sciences",
    "Journal of Sport and Health Science",
    "Sports Medicine-Open",
    
    # 营养/行为类
    "International Journal of Sport Nutrition and Exercise Metabolism",
    "Journal of the International Society of Sports Nutrition",
    "International Journal of Behavioral Nutrition and Physical Activity",
    "Nutrients"
]

# --- 辅助函数 ---

def translate_to_chinese(text, retries=3):
    """Google Translate Web API with simple retry logic"""
    if not text: return ""
    
    # 预处理：保持段落结构，但去除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > TRANSLATION_LIMIT: text = text[:TRANSLATION_LIMIT] + "..."
    
    url = "https://translate.googleapis.com/translate_a/single"
    params = {"client": "gtx", "sl": "auto", "tl": "zh-CN", "dt": "t", "q": text}
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                # 拼接翻译结果
                return "".join([x[0] for x in data[0] if x[0]])
        except Exception as e:
            if attempt == retries - 1:
                print(f"    ⚠️ Translation failed after {retries} attempts: {e}")
                return text # Fallback to original
            time.sleep(1)
            
    return text

def is_recent(entry_date_struct, days):
    """Check if date is within lookback period"""
    if not entry_date_struct: return False
    now = datetime.datetime.now(timezone.utc)
    try:
        # entry_date_struct usually is time.struct_time
        # convert to aware datetime
        pub_date = datetime.datetime(*entry_date_struct[:6], tzinfo=timezone.utc)
        delta = now - pub_date
        return delta.days < days
    except:
        return False # Fail safe

# 历史记录文件
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'processed_history.json')

def load_history():
    """Load processed links from history file"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception as e:
            print(f"    ⚠️ Warning: Could not load history: {e}")
            return set()
    return set()

def save_history(history_set):
    """Save processed links to history file"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(history_set), f, indent=2)
    except Exception as e:
        print(f"    ⚠️ Warning: Could not save history: {e}")

# --- 核心抓取 ---

def fetch_rss_feeds(days, history_set, disable_history=False):
    print("📡 正在抓取精选专家源 (RSS)...")
    content = {}
    new_links = set()
    
    for category, feeds in RSS_FEEDS.items():
        print(f"  📂 {category}")
        items = []
        for name, url in feeds:
            try:
                # Robust Fetching with User-Agent
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/rss+xml, application/xml, text/xml, */*'
                })
                try:
                    with urllib.request.urlopen(req, timeout=15) as response:
                        xml_content = response.read()
                        feed = feedparser.parse(xml_content)
                except Exception as net_err:
                    print(f"    ⚠️ Network/Auth Error for {name}: {net_err} - Trying direct parse...")
                    feed = feedparser.parse(url) # Fallback

                if feed.bozo and feed.bozo_exception:
                    # Ignore common encoding errors if entries exist
                    if len(feed.entries) == 0:
                        print(f"    ⚠️ Feed Parse Error (BOZO) for {name}: {feed.bozo_exception}")
                        continue
                
                count = 0
                for entry in feed.entries:
                    if count >= ITEMS_PER_FEED: break
                    
                    try:
                        # Date Check
                        date_struct = getattr(entry, 'published_parsed', None) or getattr(entry, 'updated_parsed', None)
                        if not is_recent(date_struct, days): continue
                        
                        # Safe Link Parsing (Fix for Huberman/others)
                        link = getattr(entry, 'link', '')
                        if not link and hasattr(entry, 'links'):
                            for l in entry.links:
                                if l.get('rel') == 'alternate':
                                    link = l.get('href')
                                    break
                        
                        if not link:
                            # print(f"    ⚠️ Skipping entry with no link: {getattr(entry, 'title', 'No Title')[:30]}")
                            continue
                        
                        # Deduplication Check
                        if not disable_history and link in history_set:
                            # print(f"    ℹ️ Skipping (Already processed): {entry.title[:30]}...")
                            continue
                        
                        title = getattr(entry, 'title', 'No Title')
                        
                        summary = ""
                        if hasattr(entry, 'summary'): summary = entry.summary
                        elif hasattr(entry, 'description'): summary = entry.description
                        elif hasattr(entry, 'media_description'): summary = entry.media_description
                        
                        # 优先处理 YouTube 视频描述
                        if hasattr(entry, 'media_group'):
                            media_desc = entry.media_group.get('media_description', '')
                            if media_desc:
                                summary = media_desc
                        
                        # Clean HTML for translation
                        clean_summary = re.sub(r'<[^>]+>', ' ', summary)
                        clean_summary = " ".join(clean_summary.split())[:500] 
                        
                        print(f"    Processing: {title[:30]}...")
                        title_zh = translate_to_chinese(title)
                        summary_zh = translate_to_chinese(clean_summary)
                        
                        items.append({
                            'title': title_zh,
                            'orig_title': title,
                            'link': link,
                            'summary': summary_zh,
                            'orig_summary': summary, # Store original for filtering
                            'source': name
                        })
                        new_links.add(link)
                        count += 1
                        
                    except Exception as e:
                        print(f"    ⚠️ Error processing entry from {name}: {e}")
                        continue
            except Exception as e:
                print(f"    ⚠️ Error fetching {name}: {e}")
        
        if items: content[category] = items
        
    return content, new_links

def fetch_pubmed_abstracts(days, history_set, disable_history=False):
    print(f"📚 正在深度抓取 PubMed 顶刊论文 (Last {days} days)...")
    
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    # --- PubMed Blocklist (Exclude Surgery/Animals) ---
    PUBMED_BLOCKLIST = [
        "rat", "rats", "mouse", "mice", "murine", "animal", "porcine", "cadaver", "cadaveric", "vitro",
        "surgery", "surgical", "reconstruction", "arthroscopy", "arthroplasty", "graft", "implant", "prosthesis",
        "cancer", "chemotherapy", "tumor", "metastasis", "oncology"
    ]
    pubmed_block_pattern = re.compile(
        r'\b(' + '|'.join(map(re.escape, PUBMED_BLOCKLIST)) + r')\b',
        re.IGNORECASE
    )
    
    # 1. Search
    journal_query = " OR ".join([f'"{j}"[Journal]' for j in PUBMED_JOURNALS])
    # Add date filter
    query = f'({journal_query}) AND ("last {days} days"[dp])'
    
    search_url = f"{base_url}/esearch.fcgi?db=pubmed&term={urllib.parse.quote(query)}&retmode=json&retmax={RETMAX_PUBMED}"
    
    new_links = set()
    
    try:
        req = urllib.request.Request(search_url)
        with urllib.request.urlopen(req) as r:
            data = json.loads(r.read().decode('utf-8'))
            id_list = data.get('esearchresult', {}).get('idlist', [])
            
        if not id_list:
            print("    ℹ️ 没有发现新论文")
            return [], new_links
        
        # Filter IDs based on history (link construction: https://pubmed.ncbi.nlm.nih.gov/{pmid}/)
        unique_id_list = []
        for pmid in id_list:
            link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            if not disable_history and link in history_set:
                continue
            unique_id_list.append(pmid)
            
        if not unique_id_list:
             print("    ℹ️ 所有新论文均已处理过。")
             return [], new_links

        print(f"    🔍 发现 {len(unique_id_list)} 篇新论文 (总数 {len(id_list)})，正在解析摘要...")
        
        # 2. Fetch Details (XML)
        ids = ",".join(unique_id_list)
        fetch_url = f"{base_url}/efetch.fcgi?db=pubmed&id={ids}&retmode=xml"
        
        req = urllib.request.Request(fetch_url)
        papers = []
        with urllib.request.urlopen(req) as r:
            tree = ET.fromstring(r.read())
            
            for article in tree.findall(".//PubmedArticle"):
                try:
                    # Basic Info
                    title = article.findtext(".//ArticleTitle") or "No Title"
                    journal = article.findtext(".//Journal/Title") or "Unknown Journal"
                    pmid = article.findtext(".//PMID")
                    if not pmid: continue
                    link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    
                    # Abstract Parsing (Structured)
                    abstract_parts = []
                    abstract_texts = article.findall(".//AbstractText")
                    
                    if abstract_texts:
                        for elem in abstract_texts:
                            label = elem.get('Label') # e.g., BACKGROUND, METHODS, RESULTS
                            text = elem.text
                            if not text: continue
                            
                            if label:
                                abstract_parts.append(f"**{label.title()}**: {text}")
                            else:
                                abstract_parts.append(text)
                        full_abstract = "\n\n".join(abstract_parts)
                    else:
                        full_abstract = "No abstract available."
                    
                    
                    # --- Blocklist Check ---
                    text_to_check = (title + " " + full_abstract).lower()
                    if pubmed_block_pattern.search(text_to_check):
                        print(f"    🚫 Blocked (Topic): {title[:50]}...")
                        # Add to history to prevent re-fetching
                        new_links.add(link) 
                        continue
                        
                    # Translation
                    print(f"    📄 Translating: {title[:30]}...")
                    title_zh = translate_to_chinese(title)
                    # Translate abstract paragraph by paragraph to maintain structure
                    abstract_zh_parts = []
                    for part in abstract_parts:
                        if part.startswith("**"):
                            # Handle labeled parts: "**Methods**: content"
                            split_idx = part.find(": ")
                            if split_idx != -1:
                                label_part = part[:split_idx+2]
                                content_part = part[split_idx+2:]
                                abstract_zh_parts.append(f"{label_part}{translate_to_chinese(content_part)}")
                            else:
                                abstract_zh_parts.append(translate_to_chinese(part))
                        else:
                            abstract_zh_parts.append(translate_to_chinese(part))
                    
                    abstract_zh = "\n\n".join(abstract_zh_parts) if abstract_zh_parts else translate_to_chinese(full_abstract)
                    
                    papers.append({
                        'title': title_zh,
                        'orig_title': title,
                        'source': journal,
                        'link': link,
                        'summary': abstract_zh
                    })
                    new_links.add(link)
                    
                except Exception as e:
                    print(f"    ⚠️ Error parsing paper: {e}")
                    continue
                    
        return papers, new_links
        
    except Exception as e:
        print(f"    ⚠️ PubMed Search Error: {e}")
        return [], new_links

# --- Markdown & Notion ---

def generate_markdown(rss_data, pubmed_data):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    md_lines = []
    
    md_lines.append(f"# 🧬 运动科学日报 (Research Grade) - {today}")
    md_lines.append(f"> 这里只关注最硬核的科学：PubMed 顶刊解析与专家深度博客。")
    md_lines.append("")
    
    # 1. 我喜欢的博主的动向
    md_lines.append("## 1. 我喜欢的博主的动向")
    md_lines.append("")
    
    blogger_items = rss_data.get("bloggers", [])
    if blogger_items:
        for item in blogger_items:
            md_lines.append(f"### {item['title']}")
            md_lines.append(f"**来源:** {item['source']} | [原文链接]({item['link']})")
            md_lines.append("")
            md_lines.append(f"> {item['summary']}")
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
    else:
        md_lines.append("*(今日暂无更新)*")
        md_lines.append("")

    # 2. 行业动向
    md_lines.append("## 2. 行业科研与技术工程 (Industry Research & Engineering)")
    md_lines.append("")
    
    industry_items = rss_data.get("industry", [])
    
    # 关键词过滤 (仅保留运动健康相关)
    # 关键词过滤 (仅保留运动健康相关)
    POSITIVE_KEYWORDS = [
        "health", "fitness", "sport", "run", "running", "swim", "cycle", "cycling", "ride", 
        "train", "training", "exercise", "workout", "sleep", "recovery", "rest",
        "heart", "hrv", "pulse", "oxygen", "blood", "glucose", "monitor", "vital", "stress",
        "watch", "smartwatch", "band", "ring", "wearable", "tracker", 
        "coach", "athlete", "marathon", "triathlon",
        "muscle", "cardio", "aerobic", "anaerobic", "vo2", "calorie", "step", "activity",
        "motion", "movement", "wellness", "physio", "biometric", "body",
        "metabolic", "metabolism", "altitude", "acclimation", "heat", "cold"
    ]
    
    # 必须包含的科研/硬核关键词 (User Request: Focus on Research & Technical Blogs)
    RESEARCH_KEYWORDS = [
        "research", "study", "science", "scientist", "clinical", "publication", "paper", "journal",
        "algorithm", "validation", "whitepaper", "engineering", "technology", "tech", "lab", 
        "measure", "accuracy", "biomarker", "sensor", "data", "analysis", "insight", "review",
        "deep dive", "explained", "how it works", "behind the scenes", "validity", "reliability",
        "testing", "beta", "update", "feature", "metric", "physiology",
        "ai", "artificial intelligence", "machine learning", "neural network", "deep learning", "model",
        # 可穿戴设备研究专用词
        "strain", "readiness", "load", "trend", "score", "stage", "zone", "baseline",
        "track", "detect", "predict", "alert", "notification", "insight", "optimize",
        "sleep architecture", "circadian", "rem", "deep sleep", "light sleep",
        "resting heart rate", "respiratory rate", "spo2", "temperature", "skin temp"
    ]
    
    # 受信任的厂商官方博客 (对这些源放宽过滤要求)
    TRUSTED_SOURCES = [
        "garmin", "oura", "polar", "fitbit", "whoop", "dc rainmaker",
        "google research", "apple"
    ]
    
    NEGATIVE_KEYWORDS = [
        "shareholder", "dividend", "financial results", "quarterly", "revenue", "profit",
        "phone", "phones", "smartphone", "smartphones", "mobile", "mobiles", 
        "camera", "cameras", "lens", "lenses", "laptop", "laptops", "notebook", "notebooks", 
        "tv", "tvs", "television", "televisions",
        "car", "cars", "automotive", "auto", "vehicle", "vehicles",
        "headphone", "headphones", "earbud", "earbuds", 
        "movie", "movies", "cinema", "film", "films", "motion picture",
        "video game", "gaming", "console", "consoles", 
        "music", "album", "song", "songs", "artist", "artists", "award", "awards",
        "investment", "stock", "stocks", "discount", "bundle", "clearance", "sale", "sales",
        "aviation", "cockpit", "flight", "pilot",  # Garmin Aviation
        "marathon training", "training plan", "join our", "program" # Generic Training Plans
    ]
    
    # Pre-compile regex for negative keywords (Word Boundary check)
    negative_pattern = re.compile(
        r'\b(' + '|'.join(map(re.escape, NEGATIVE_KEYWORDS)) + r')\b',
        re.IGNORECASE
    )
    
    filtered_industry_items = []
    
    for item in industry_items:
        # CRITICAL FIX: Use original English text for filtering
        text_to_check = (item.get('orig_title', '') + " " + item.get('orig_summary', '')).lower()
        if not text_to_check.strip():
             text_to_check = (item['title'] + " " + item['summary']).lower() # Fallback
        
        # 获取源名称用于白名单检查
        source_name = item.get('source', '').lower()
        is_trusted_source = any(ts in source_name for ts in TRUSTED_SOURCES)
        
        # 1. 必须包含至少一个普通关键词 (Topic)
        has_positive = any(pk in text_to_check for pk in POSITIVE_KEYWORDS)
        
        # 2. 必须包含至少一个科研/硬核关键词 (Depth)
        has_research = any(rk in text_to_check for rk in RESEARCH_KEYWORDS)

        # 3. 不能包含任何负面关键词
        has_negative = bool(negative_pattern.search(text_to_check))
        
        # 豁免逻辑：对受信任源放宽深度要求
        STRONG_KEYWORDS = ["validation", "accuracy", "algorithm", "whitepaper"]
        has_strong = any(sk in text_to_check for sk in STRONG_KEYWORDS)
        
        if has_negative and not has_strong:
            is_relevant = False
        else:
            # 核心逻辑升级:
            # - 受信任源: 只要有 Topic 关键词即可 (放宽 Depth 要求)
            # - 其他源: 必须同时有 Topic + Depth
            if is_trusted_source:
                is_relevant = has_positive  # 受信任源放宽: 只需 Topic
            else:
                is_relevant = has_positive and (has_research or has_strong)
            
        if is_relevant:
            filtered_industry_items.append(item)
        else:
            print(f"    ❌ Rejected: {item.get('orig_title', item['title'])[:30]}... (Pos:{has_positive}, Res:{has_research}, Str:{has_strong}, Trusted:{is_trusted_source})")
    
    if filtered_industry_items:
        for item in filtered_industry_items:
            # Check if title/summary needs translation (it hasn't been translated yet in the main flow)
            title = item['title']
            summary = item['summary']
            
            md_lines.append(f"### {translate_to_chinese(title)}")
            md_lines.append(f"**来源:** {item['source']} | [原文链接]({item['link']})")
            md_lines.append("")
            md_lines.append(f"> {translate_to_chinese(summary)}")
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
    else:
        md_lines.append("*(今日暂无更新)*")
        md_lines.append("")

    # 3. 科研进展
    md_lines.append("## 3. 科研进展 (PubMed 顶刊)")
    md_lines.append("")
    
    if pubmed_data:
        for paper in pubmed_data:
            md_lines.append(f"### {paper['title']}")
            md_lines.append(f"**期刊:** *{paper['source']}* | [原文链接]({paper['link']})")
            md_lines.append("")
            md_lines.append(paper['summary'])
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
    else:
        md_lines.append("*(今日暂无新发表论文)*")
        md_lines.append("")
            
    return "\n".join(md_lines)

def parse_markdown_to_notion_blocks(markdown_text):
    """
    Improved Markdown parser for Notion blocks.
    Handles headers, bold, links, and paragraphs.
    """
    blocks = []
    lines = markdown_text.split('\n')
    
    current_paragraph = []
    
    for line in lines:
        line = line.rstrip() # keep leading spaces if needed, but remove trailing
        
        # If empty line, flush paragraph
        if not line:
            if current_paragraph:
                text_content = "\n".join(current_paragraph)
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": parse_rich_text(text_content)}
                })
                current_paragraph = []
            continue
            
        # Check for Headers or Divider
        if line.startswith("# ") or line.startswith("## ") or line.startswith("### ") or line.startswith("---"):
            # Flush previous paragraph first
            if current_paragraph:
                text_content = "\n".join(current_paragraph)
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": parse_rich_text(text_content)}
                })
                current_paragraph = []
                
            if line.startswith("# "):
                pass # Main title skipped
            elif line.startswith("## "):
                blocks.append({"object": "block", "type": "heading_2", "heading_2": {"rich_text": parse_rich_text(line[3:])}})
            elif line.startswith("### "):
                blocks.append({"object": "block", "type": "heading_3", "heading_3": {"rich_text": parse_rich_text(line[4:])}})
            elif line.startswith("---"):
                blocks.append({"object": "block", "type": "divider", "divider": {}})
        
        elif line.startswith("> "):
            # Blockquote
             if current_paragraph:
                text_content = "\n".join(current_paragraph)
                blocks.append({"object": "block", "type": "paragraph", "paragraph": {"rich_text": parse_rich_text(text_content)}})
                current_paragraph = []
             blocks.append({"object": "block", "type": "quote", "quote": {"rich_text": parse_rich_text(line[2:])}})
        
        else:
            # Accumulate paragraph lines
            current_paragraph.append(line)
            
    # Flush remaining
    if current_paragraph:
        text_content = "\n".join(current_paragraph)
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": parse_rich_text(text_content)}
        })

    return blocks

def parse_rich_text(text):
    """
    Parses **bold** and [link](url).
    """
    parts = []
    # Regex for [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\((http[^\)]+)\)')
    # Regex for **bold**
    bold_pattern = re.compile(r'\*\*([^\*]+)\*\*')
    
    # We will split by links first, then process bold inside non-link parts
    last_idx = 0
    for match in link_pattern.finditer(text):
        pre_text = text[last_idx:match.start()]
        if pre_text:
            parts.extend(process_bold(pre_text, bold_pattern))
            
        link_text = match.group(1)
        link_url = match.group(2)
        parts.append({
            "type": "text",
            "text": {"content": link_text, "link": {"url": link_url}}
        })
        last_idx = match.end()
        
    if last_idx < len(text):
        parts.extend(process_bold(text[last_idx:], bold_pattern))
        
    return parts

def process_bold(text, pattern):
    results = []
    last_idx = 0
    for match in pattern.finditer(text):
        pre = text[last_idx:match.start()]
        if pre: results.append({"type": "text", "text": {"content": pre}})
        
        bold_content = match.group(1)
        results.append({
            "type": "text",
            "text": {"content": bold_content},
            "annotations": {"bold": True}
        })
        last_idx = match.end()
        
    if last_idx < len(text):
        results.append({"type": "text", "text": {"content": text[last_idx:]}})
    return results

def sync_to_notion(blocks, token, page_id):
    if not token or not page_id:
        print("ℹ️ Notion Token 或 Page ID 未设置，跳过上传。")
        print("   (请设置环境变量 NOTION_TOKEN 和 NOTION_PAGE_ID 在 setup_cron.sh 中)")
        return

    print("🔄 同步到 Notion...")
    
    def notion_request(endpoint, data, method="POST"):
        url = f"https://api.notion.com/v1/{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method=method)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"   ❌ Notion API Error: {e.code} - {e.read().decode('utf-8')}")
            return None

    # 1. Create Page
    today_title = f"🧬 运动科学日报 (Research Grade) - {datetime.datetime.now().strftime('%Y-%m-%d')}"
    resp = notion_request("pages", {
        "parent": {"page_id": page_id},
        "properties": {"title": {"title": [{"text": {"content": today_title}}]}}
    })
    
    if not resp: return
    new_page_id = resp['id']
    
    # 2. Upload in batches
    batch_size = 90
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        notion_request(f"blocks/{new_page_id}/children", {"children": batch}, method="PATCH")
        print(f"   已上传 {len(batch)} 个区块...")
        
    print(f"✨ 同步完成！页面: https://notion.so/{new_page_id.replace('-', '')}")

# --- 主程序 ---

def main():
    parser = argparse.ArgumentParser(description="Sports Science Daily Crawler")
    parser.add_argument("--days", type=int, default=7, help="Lookback days for new content (default: 7)")
    parser.add_argument("--no-history", action="store_true", help="Disable history checking (fetching all items)")
    args = parser.parse_args()
    
    print(f"🚀 启动运动科学爬虫 V3.1 (Deduplication Enabled) - Lookback: {args.days} days")
    
    history_set = load_history()
    print(f"📚 已加载 {len(history_set)} 条历史记录")
    
    rss_data, rss_new_links = fetch_rss_feeds(args.days, history_set, args.no_history)
    pubmed_data, pubmed_new_links = fetch_pubmed_abstracts(args.days, history_set, args.no_history)
    
    # 检查是否有新内容
    total_new = len(rss_new_links) + len(pubmed_new_links)
    if total_new == 0:
        print("🎉 没有发现新内容 (所有项目均已在之前的运行中处理过)。")
        return

    md_content = generate_markdown(rss_data, pubmed_data)
    
    # Save local file
    filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_运动科学日报.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"💾 本地文件已保存: {filename}")
    
    # Notion Sync
    blocks = parse_markdown_to_notion_blocks(md_content)
    sync_to_notion(blocks, NOTION_TOKEN, NOTION_PAGE_ID)
    
    # Update History
    if not args.no_history:
        history_set.update(rss_new_links)
        history_set.update(pubmed_new_links)
        save_history(history_set)
        print(f"🔖 更新历史记录: 新增 {total_new} 条项目，总计 {len(history_set)} 条。")

if __name__ == "__main__":
    main()
