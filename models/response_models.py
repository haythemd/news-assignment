from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Article(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image: Optional[str] = None
    publishedAt: str
    source: Dict[str, Any]

class BaseResponse(BaseModel):
    success: bool = True
    from_cache: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

class NewsResponse(BaseResponse):
    totalArticles: int
    articles: List[Article]

class SearchResponse(BaseResponse):
    totalArticles: int
    articles: List[Article]

class CacheStatsResponse(BaseModel):
    keys: int
    hits: int
    misses: int
    hit_rate: float
    cache_size: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    cache_keys: int
    api_key_configured: bool

class APIDocsResponse(BaseModel):
    message: str
    documentation: str
    health_check: str
    version: str
    author: str