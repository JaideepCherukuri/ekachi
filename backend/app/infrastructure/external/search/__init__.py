from functools import lru_cache
from typing import Optional
import logging

from app.domain.external.search import SearchEngine
from app.core.config import get_settings

logger = logging.getLogger(__name__)

def create_search_engine(provider: Optional[str] = None) -> Optional[SearchEngine]:
    """Create a search engine instance for the given provider or the configured default."""
    from app.infrastructure.external.search.google_search import GoogleSearchEngine
    from app.infrastructure.external.search.baidu_search import BaiduSearchEngine
    from app.infrastructure.external.search.baidu_web_search import BaiduWebSearchEngine
    from app.infrastructure.external.search.bing_search import BingSearchEngine
    from app.infrastructure.external.search.bing_web_search import BingWebSearchEngine
    from app.infrastructure.external.search.tavily_search import TavilySearchEngine
    
    settings = get_settings()
    selected_provider = provider if provider is not None else settings.search_provider
    if selected_provider == "google":
        if settings.google_search_api_key and settings.google_search_engine_id:
            logger.info("Initializing Google Search Engine")
            return GoogleSearchEngine(
                api_key=settings.google_search_api_key,
                cx=settings.google_search_engine_id
            )
        else:
            logger.warning("Google Search Engine not initialized: missing API key or engine ID")
    elif selected_provider == "baidu":
        if settings.baidu_search_api_key:
            logger.info("Initializing Baidu Search Engine (API)")
            return BaiduSearchEngine(api_key=settings.baidu_search_api_key)
        else:
            logger.warning("Baidu Search Engine not initialized: missing API key (BAIDU_SEARCH_API_KEY)")
    elif selected_provider == "baidu_web":
        logger.info("Initializing Baidu Web Search Engine (scraping)")
        return BaiduWebSearchEngine()
    elif selected_provider == "bing":
        if settings.bing_search_api_key:
            logger.info("Initializing Bing Search Engine (API)")
            return BingSearchEngine(api_key=settings.bing_search_api_key)
        else:
            logger.warning("Bing Search Engine not initialized: missing API key (BING_SEARCH_API_KEY)")
    elif selected_provider == "bing_web":
        logger.info("Initializing Bing Web Search Engine (scraping)")
        return BingWebSearchEngine()
    elif selected_provider == "tavily":
        if settings.tavily_api_key:
            logger.info("Initializing Tavily Search Engine")
            return TavilySearchEngine(api_key=settings.tavily_api_key)
        else:
            logger.warning("Tavily Search Engine not initialized: missing API key")
    else:
        logger.warning(f"Unknown search provider: {selected_provider}")
    
    return None


@lru_cache()
def get_search_engine() -> Optional[SearchEngine]:
    """Get cached default search engine instance based on configuration."""
    return create_search_engine()
