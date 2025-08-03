import httpx
import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from cachetools import TTLCache
import asyncio
from datetime import datetime

class NewsService:
    def __init__(self):
        # Initialize cache with 10-minute TTL (600 seconds) and max 1000 items
        self.cache = TTLCache(maxsize=1000, ttl=600)
        self.base_url = "https://gnews.io/api/v4"
        self.api_key = os.getenv("GNEWS_API_KEY")
        self.cache_hits = 0
        self.cache_misses = 0
        
        if not self.api_key:
            print("Warning: GNEWS_API_KEY not found in environment variables")
    
    def _generate_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate a unique cache key based on endpoint and parameters"""
        # Sort parameters for consistent key generation
        sorted_params = dict(sorted(params.items()))
        key_string = f"{endpoint}_{json.dumps(sorted_params, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with caching"""
        cache_key = self._generate_cache_key(endpoint, params)
        
        # Check cache first
        if cache_key in self.cache:
            self.cache_hits += 1
            cached_data = self.cache[cache_key]
            print(f"Cache hit for key: {cache_key}")
            return {**cached_data, "from_cache": True}
        
        # Add API key to parameters
        params_with_key = {**params, "apikey": self.api_key}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/{endpoint}",
                    params=params_with_key
                )
                response.raise_for_status()
                data = response.json()
                
                # Cache the response
                self.cache[cache_key] = data
                self.cache_misses += 1
                print(f"Cache miss - stored data for key: {cache_key}")
                
                return {**data, "from_cache": False}
                
        except httpx.HTTPStatusError as e:
            error_msg = f"GNews API Error: {e.response.status_code}"
            try:
                error_detail = e.response.json().get("message", "Unknown error")
                error_msg += f" - {error_detail}"
            except:
                pass
            raise Exception(error_msg)
        except httpx.RequestError as e:
            raise Exception(f"Network error: Unable to reach GNews API - {str(e)}")
        except Exception as e:
            raise Exception(f"Request error: {str(e)}")
    
    async def get_top_headlines(
        self, 
        count: int = 10, 
        lang: str = "en",
        country: str = "us", 
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch top headlines"""
        params = {
            "max": min(count, 100),  # GNews API limit
            "country": country,
            "lang": lang
        }
        
        if category:
            params["category"] = category
        
        return await self._make_request("top-headlines", params)
    
    async def search_articles(
        self,
        query: str,
        count: int = 10,
        language: str = "en",
        country: str = "us",
        sort_by: str = "relevance"
    ) -> Dict[str, Any]:
        """Search articles by keywords"""
        params = {
            "q": query,
            "max": min(count, 100),
            "lang": language,
            "country": country,
            "sortby": sort_by
        }
        
        return await self._make_request("search", params)
    
    async def find_by_title(self, title: str, exact: bool = False) -> Dict[str, Any]:
        """Find articles by title"""
        query = f'"{title}"' if exact else title
        result = await self.search_articles(query, 50)
        
        if "articles" in result:
            # Filter results for better title matching
            filtered_articles = []
            search_title = title.lower()
            
            for article in result["articles"]:
                article_title = article["title"].lower()
                
                match = (
                    article_title == search_title if exact 
                    else search_title in article_title
                )
                
                if match:
                    filtered_articles.append(article)
            
            result["articles"] = filtered_articles
            result["totalArticles"] = len(filtered_articles)
        
        return result
    
    async def find_by_author(self, author: str, count: int = 10) -> Dict[str, Any]:
        """Find articles by author or source"""
        # Search broadly first
        result = await self.search_articles(author, 100)
        
        if "articles" in result:
            # Filter by source name
            filtered_articles = []
            author_lower = author.lower()
            
            for article in result["articles"]:
                if (article.get("source") and 
                    article["source"].get("name") and
                    author_lower in article["source"]["name"].lower()):
                    filtered_articles.append(article)
                    
                    if len(filtered_articles) >= count:
                        break
            
            result["articles"] = filtered_articles
            result["totalArticles"] = len(filtered_articles)
        
        return result
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            "keys": len(self.cache),
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": round(hit_rate, 3),
            "cache_size": len(self.cache)
        }
    
    def clear_cache(self) -> Dict[str, str]:
        """Clear the cache"""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        return {"message": "Cache cleared successfully"}