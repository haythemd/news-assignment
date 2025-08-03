from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from services.news_service import NewsService

from models.response_models import (
    NewsResponse, 
    SearchResponse, 
    CacheStatsResponse, 
    HealthResponse,
    APIDocsResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="News API Assignment",
    description="Haythem DRIHMI take-home assignment",
    version="0.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize news service
news_service = NewsService()

@app.get("/", response_model=APIDocsResponse)
async def root():
    """Root endpoint with API information"""
    return APIDocsResponse(
        message="Welcome to News API Service",
        documentation="/docs",
        health_check="/health",
        version="0.0.1",
        author='Haythem DRIHMI'
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    cache_stats = news_service.get_cache_stats()
    return HealthResponse(
        status="healthy",
        cache_keys=cache_stats["keys"],
        api_key_configured=bool(os.getenv("GNEWS_API_KEY"))
    )

@app.get("/api/news/headlines", response_model=NewsResponse)
async def get_headlines(
    count: int = Query(default=10, ge=1, le=100, description="Number of articles to fetch"),
    country: str = Query(default="us", description="Country code (us, uk, ca, etc.)"),
    language: str = Query(default="en", description="Language code (en, es, fr, etc.)"),
    category: str = Query(default=None, description="Category filter (general, world, business, etc.)")
):
    """
    Fetch top headlines from news sources
    
    - **count**: Number of articles (1-100)
    - **lang**: Language of news sources
    - **country**: Country code for news sources
    - **category**: News category filter

    Note that pagination is only included in paid subscriptions.
    """
    try:
        result = await news_service.get_top_headlines(count,language , country, category)
        return NewsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/search", response_model=SearchResponse)
async def search_articles(
    q: str = Query(description="Search query keywords"),
    count: int = Query(default=10, ge=1, le=100, description="Number of articles to fetch"),
    language: str = Query(default="en", description="Language code (en, es, fr, etc.)"),
    country: str = Query(default="us", description="Country code (us, uk, ca, etc.)"),
    sort_by: str = Query(default="relevance", description="Sort by: relevance or publishedAt")
):
    """
    Search for articles using keywords
    
    - **q**: Search query (required)
    - **count**: Number of articles (1-100)  
    - **language**: Language code
    - **country**: Country code for news sources
    - **sort_by**: Sort order (relevance or publishedAt)
    """
    try:
        result = await news_service.search_articles(q, count, language, country, sort_by)
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/title/{title}", response_model=SearchResponse)
async def find_by_title(
    title: str = Path(description="Article title to search for"),
    exact: bool = Query(default=False, description="Exact title matching")
):
    """
    Find articles by title
    
    - **title**: Article title to search for
    - **exact**: Whether to use exact matching
    """
    try:
        result = await news_service.find_by_title(title, exact)
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/author/{author}", response_model=SearchResponse)
async def find_by_author(
    author: str = Path(description="Author or source name"),
    count: int = Query(default=10, ge=1, le=100, description="Number of articles to fetch")
):
    """
    Find articles by author or news source
    
    - **author**: Author or source name to search for
    - **count**: Number of articles to return
    """
    try:
        result = await news_service.find_by_author(author, count)
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/cache/stats", response_model=CacheStatsResponse)
async def get_cache_stats():
    """Get cache performance statistics"""
    try:
        stats = news_service.get_cache_stats()
        return CacheStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/news/cache")
async def clear_cache():
    """Clear the cache"""
    try:
        result = news_service.clear_cache()
        return JSONResponse(content={"success": True, "message": result["message"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )