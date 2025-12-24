"""Simple in-memory cache for YouTube search results."""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('discord_music_bot')


class SearchCache:
    """Cache YouTube search results to avoid duplicate searches."""
    
    def __init__(self, ttl_hours=2):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
        self.hits = 0
        self.misses = 0
    
    def get(self, query):
        """Get cached result if exists and not expired."""
        query_lower = query.lower().strip()
        
        if query_lower in self.cache:
            result, timestamp = self.cache[query_lower]
            
            if datetime.now() - timestamp < self.ttl:
                self.hits += 1
                return result
            else:
                del self.cache[query_lower]
        
        self.misses += 1
        return None
    
    def set(self, query, result):
        """Cache a search result."""
        query_lower = query.lower().strip()
        self.cache[query_lower] = (result, datetime.now())
    
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self):
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }


# Global cache instance
search_cache = SearchCache(ttl_hours=2)
