# news_client.py. Service functions for news client router

from datetime import datetime, timedelta
import httpx
from config import settings

# Exception for news api errors
class NewsAPIError(Exception):
    pass

# NewsClient class for news api client to get articles
class NewsClient():
# service metod to get articles
    async def fetch_articles(self,
                             topic:str,
                             days:int,
                             language:str,  #"en"|"ru"
                             max_articles:int):

# Calculate date to start serch
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

# Request to news api for data with requested parameters
        async with httpx.AsyncClient(timeout=15.0) as client:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": topic,
                "from": from_date,
                "language": language,
                "pageSize": max_articles,
                "apiKey": settings.news_api_key}

# Waiting for response
            response = await client.get(url, params=params)

# Exception if response is not OK via status_code
            if response.status_code != 200:
                raise NewsAPIError(f"News API returned:{response.status_code}: {response.text}")
            data = response.json()

# Exception if response is not OK via data recieved
            if data.get("status") != "ok":
                raise NewsAPIError(f"News API error: {data.get('message', 'unknown error')}")
            
# Extracting raw articles from response
            articles_raw = data.get("articles", [])

# Formatting raw articles into articles with required fields
            articles = [
                {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source",{}).get("name", "Unknown"),
                }
                for article in articles_raw

# Filtering articles with empty or "[Removed]" titles
                if article.get("title") and article.get("title") != "[Removed]"
            ]
        return articles

news_client = NewsClient()