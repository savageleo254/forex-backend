import os
import feedparser
import requests
from datetime import datetime
from alerts.telegram_alerts import send_telegram_message

NEWS_FEEDS = [
    "https://www.forexfactory.com/ff_calendar_thisweek.xml",
    # Add more feeds
]

def fetch_and_parse_news():
    all_news = []
    for url in NEWS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            news_item = {
                "title": entry.title,
                "summary": getattr(entry, "summary", ""),
                "published": entry.published,
                "link": entry.link,
            }
            all_news.append(news_item)
            # Optionally send urgent news to Telegram
            if "FOMC" in entry.title or "ECB" in entry.title:
                send_telegram_message(f"High-impact news: {entry.title}\n{entry.link}")
    return all_news

if __name__ == "__main__":
    news = fetch_and_parse_news()
    print(news[:3])