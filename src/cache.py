"""
Simple Caching Layer for Growth Engine

Provides in-memory caching with TTL for opportunity data.
In production, this would be replaced with Redis or similar.
"""

import time
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry['expires_at']:
            # Expired, remove it
            del self._cache[key]
            return None
        
        entry['last_accessed'] = time.time()
        return entry['data']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self._default_ttl
        
        self._cache[key] = {
            'data': value,
            'created_at': time.time(),
            'expires_at': time.time() + ttl,
            'last_accessed': time.time()
        }
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()
    
    def keys(self) -> list:
        """Get all cache keys"""
        return list(self._cache.keys())
    
    def size(self) -> int:
        """Get number of cached items"""
        return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        active_entries = sum(1 for entry in self._cache.values() 
                           if current_time <= entry['expires_at'])
        expired_entries = len(self._cache) - active_entries
        
        return {
            'total_entries': len(self._cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries,
            'hit_rate': getattr(self, '_hits', 0) / max(getattr(self, '_requests', 1), 1),
            'memory_usage_mb': len(json.dumps(self._cache, default=str)) / 1024 / 1024
        }


# Global cache instance
_global_cache = SimpleCache()


def get_cache() -> SimpleCache:
    """Get the global cache instance"""
    return _global_cache


class CachedOpportunityManager:
    """Manages cached opportunities with smart invalidation"""
    
    def __init__(self):
        self.cache = get_cache()
        self.batch_cache_ttl = 1800  # 30 minutes for batch results
        self.search_cache_ttl = 300   # 5 minutes for search results
    
    def get_batch_opportunities(self, batch_id: str) -> Optional[Dict]:
        """Get cached opportunities for a batch"""
        cache_key = f"batch:{batch_id}"
        return self.cache.get(cache_key)
    
    def set_batch_opportunities(self, batch_id: str, opportunities: Dict) -> None:
        """Cache opportunities for a batch"""
        cache_key = f"batch:{batch_id}"
        self.cache.set(cache_key, opportunities, self.batch_cache_ttl)
    
    def get_search_results(self, query: str, filters: Dict) -> Optional[Dict]:
        """Get cached search results"""
        cache_key = f"search:{hash(f'{query}:{json.dumps(filters, sort_keys=True)}'.encode())}"
        return self.cache.get(cache_key)
    
    def set_search_results(self, query: str, filters: Dict, results: Dict) -> None:
        """Cache search results"""
        cache_key = f"search:{hash(f'{query}:{json.dumps(filters, sort_keys=True)}'.encode())}"
        self.cache.set(cache_key, results, self.search_cache_ttl)
    
    def invalidate_batch(self, batch_id: str) -> bool:
        """Invalidate cached batch data"""
        cache_key = f"batch:{batch_id}"
        return self.cache.delete(cache_key)
    
    def clear_search_cache(self) -> None:
        """Clear all search result caches"""
        search_keys = [key for key in self.cache.keys() if key.startswith('search:')]
        for key in search_keys:
            self.cache.delete(key)


# Global opportunity cache manager
opportunity_cache = CachedOpportunityManager()