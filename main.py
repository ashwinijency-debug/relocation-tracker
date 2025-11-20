import feedparser
import requests
import json
import os
from datetime import datetime
import re

def scrape_rss_feeds():
    """Get articles from news sources"""
    print("📰 Fetching news from RSS feeds...")
    
    RSS_FEEDS = [
        # Manufacturing & Industrial
        'https://www.manufacturingdive.com/feeds/news/',
        'https://www.industryweek.com/rss',
        'https://www.packagingdive.com/feeds/news/',
        
        # India Business News
        'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
        'https://economictimes.indiatimes.com/tech/technology/rssfeeds/13357270.cms',
        'https://economictimes.indiatimes.com/news/company/corporate-trends/rssfeeds/13358262.cms',
        'https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms',
        'https://timesofindia.indiatimes.com/business/rssfeeds/1898055.cms',
        'https://www.business-standard.com/rss/latest.rss',
        'https://www.thehindubusinessline.com/news/rss/rss.xml',
        'https://www.livemint.com/rss/companies',
        'https://www.moneycontrol.com/rss/business.xml',
        
        # US Business News
        'https://www.reuters.com/business/rss',
        'https://www.cnbc.com/id/10001147/device/rss/rss.html',
        
        # Commercial Real Estate
        'https://therealdeal.com/feed/',
        'https://www.cpexecutive.com/feed/',
        
        # Regional Business Journals (US)
        'https://www.bizjournals.com/feeds/rss/business_news.xml',
        'https://www.bizjournals.com/atlanta/feeds/rss/business_news.xml',
        'https://www.bizjournals.com/dallas/feeds/rss/business_news.xml',
        'https://www.bizjournals.com/sanfrancisco/feeds/rss/business_news.xml',
        'https://www.bizjournals.com/newyork/feeds/rss/business_news.xml',
        
        # Press Releases (Official Announcements)
        'https://www.prnewswire.com/rss/news-releases-list.rss',
        
        # Tech News
        'https://techcrunch.com/feed/',
        'https://www.theverge.com/rss/index.xml',
        
        # Supply Chain & Logistics
        'https://www.supplychaindive.com/feeds/news/',
        'https://www.freightwaves.com/news/feed',
    ]
    
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', entry.get('description', ''))
                })
        except Exception as e:
            print(f"❌ Error with {feed_url}: {e}")
    
    print(f"✅ Collected {len(articles)} articles from {len(RSS_FEEDS)} sources")
    return articles

def check_with_gemini(article):
    """Use Google Gemini AI to check if article is about relocation"""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("⚠️ No Gemini API key found")
        return False
    
    # Quick keyword pre-filter to save API calls
    text = (article['title'] + ' ' + article.get('summary', '')).lower()
    keywords = [
        'relocat', 'shift', 'move', 'moving', 'moved from', 'moved to', 'relocating', 
        'transferred', 'hq shift', 'headquarters move', 'office move', 'transfers headquarters',
        'shifted office', 'shifted hq', 'branch moved', 'facility shift', 'plant relocated'
    ]
    if not any(keyword in text for keyword in keywords):
        return False

    # Strict Gemini prompt:
    prompt = """
Is this article specifically about a company physically relocating (moving) their headquarters, main office, branch office, or manufacturing facility from one city/state/country to another?
Only answer YES if:
- An existing company moves, relocates, or transfers its main place of business OR factory OR office from one specific location to a different one.
- Headlines or text clearly state “moved from”, “relocated from/to”, “shifted office/plants from”, “transferred headquarters”, or similar.
Answer NO if:
- The article is only about expansion, opening a new office/facility with no mention of closing or moving the previous one.
- It’s about hiring, policy, government news, climate, business partnerships, or any topic that is NOT a physical move from one location to another.
Return only YES or NO.

Title: {title}
Summary: {summary}

Answer (YES or NO only):
""".format(title=article['title'], summary=article.get('summary', '')[:400])

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 10
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            answer = result['candidates'][0]['content']['parts'][0]['text'].strip().upper()
            return 'YES' in answer
        else:
            print(f"⚠️ Gemini API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Gemini error: {e}")
        return False

def extract_company_info(article):
    """Extract company name, locations, and other details"""
    text = article['title'] + ' ' + article.get('summary', '')
    
    # Extract company name
    company_patterns = [
        r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}(?:\s+(?:Inc|Corp|Ltd|LLC|Company|Technologies|Systems|Industries|Group))?)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:is|will|has|announced)',
    ]
    
    company = None
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1)
            break
    
    # Extract locations
    location_patterns = [
        r'(?:moving to|relocating to|shifting to|transferring to)\s+([A-Z][a-z]+(?:,?\s+[A-Z][a-z]+)*)',
        r'(?:from)\s+([A-Z][a-z]+)(?:\s+to\s+)([A-Z][a-z]+)',
        r'(?:in|at)\s+([A-Z][a-z]+(?:,\s*[A-Z]{2})?)',
    ]
    
    locations = []
    for pattern in location_patterns:
        matches = re.findall(pattern, text)
        if matches:
            if isinstance(matches[0], tuple):
                locations.extend([m for m in matches[0] if m])
            else:
                locations.extend(matches)
    
    # Remove duplicates and limit
    locations = list(set(locations))[:3]
    
    return {
        'company': company if company else 'Unknown Company',
        'locations': locations,
        'date': datetime.now().strftime('%Y-%m-%d')
    }

def load_existing_data():
    """Load previously saved relocations"""
    try:
        with open('data/relocations.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_relocations(relocations):
    """Save new relocations to file"""
    os.makedirs('data', exist_ok=True)
    
    existing = load_existing_data()
    existing_links = [x['link'] for x in existing]
    
    new_items = []
    for item in relocations:
        if item['link'] not in existing_links:
            item['scraped_at'] = datetime.now().isoformat()
            existing.append(item)
            new_items.append(item)
    
    # Keep only last 500 items
    existing = existing[-500:]
    
    with open('data/relocations.json', 'w') as f:
        json.dump(existing, f, indent=2)
    
    print(f"💾 Saved {len(new_items)} new relocations to database")
    return new_items

def send_telegram_notification(new_items):
    """Send notification via Telegram"""
    if not new_items:
        print("📱 No new items to notify")
        return
    
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("⚠️ Telegram not configured")
        return
    
    # Create message
    message = f"🔔 *{len(new_items)} New Corporate Relocation(s) Found!*\n\n"
    
    for i, item in enumerate(new_items[:5], 1):  # Max 5 per message
        info = item.get('info', {})
        message += f"*{i}. {info.get('company', 'Unknown')}*\n"
        
        if info.get('locations'):
            message += f"📍 {', '.join(info['locations'])}\n"
        
        # Shorten title if too long
        title = item['title']
        if len(title) > 100:
            title = title[:97] + "..."
        message += f"📰 {title}\n"
        message += f"🔗 [Read Full Article]({item['link']})\n"
        message += f"📅 {info.get('date', 'Today')}\n\n"
    
    if len(new_items) > 5:
        message += f"_...and {len(new_items) - 5} more. Check your GitHub repository for all results._"
    
    # Send via Telegram
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        response = requests.post(url, data={
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram notification sent successfully!")
        else:
            print(f"❌ Telegram error: {response.text}")
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {e}")

def main():
    """Main function that runs everything"""
    print("\n" + "="*60)
    print("🤖 CORPORATE RELOCATION TRACKER - POWERED BY GEMINI AI")
    print("="*60 + "\n")
    
    # Step 1: Collect articles
    articles = scrape_rss_feeds()
    
    if not articles:
        print("⚠️ No articles collected. Exiting.")
        return
    
    # Step 2: Filter for relocation articles using Gemini AI
    print("\n🔍 Analyzing articles with Gemini AI...")
    relocations = []
    
    for i, article in enumerate(articles, 1):
        print(f"Checking article {i}/{len(articles)}...", end='\r')
        
        if check_with_gemini(article):
            article['info'] = extract_company_info(article)
            relocations.append(article)
    
    print(f"\n✅ Found {len(relocations)} relocation-related articles")
    
    # Step 3: Save results
    new_items = save_relocations(relocations)
    
    # Step 4: Send notifications
    if new_items:
        print(f"\n📤 Sending notification for {len(new_items)} new items...")
        send_telegram_notification(new_items)
    else:
        print("\n📭 No new relocations found (all were already in database)")
    
    print("\n" + "="*60)
    print("✅ TRACKER COMPLETED SUCCESSFULLY")
    print("="*60 + "\n")
    
    # Print summary
    print
