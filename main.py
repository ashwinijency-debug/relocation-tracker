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
        
        # Regional Business Journals
        'https://www.bizjournals.com/feeds/rss/business_news.xml',
        'https://www.bizjournals.com/atlanta/feeds/rss/business_news.xml',
        'https://www.bizjournals.com/dallas/feeds/rss/business_news.xml',
        'https://www.bizjournals.com/sanfrancisco/feeds/rss/business_news.xml',
        
        # Press Releases
        'https://www.prnewswire.com/rss/news-releases-list.rss',
        
        # Tech News
        'https://techcrunch.com/feed/',
        'https://www.theverge.com/rss/index.xml',
        
        # Supply Chain
        'https://www.supplychaindive.com/feeds/news/',
    ]
    
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # Get 10 articles from each feed
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
