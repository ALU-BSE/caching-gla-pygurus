"""
Cache performance monitoring decorators and utilities.

This module provides decorators and utility functions for monitoring cache performance,
logging execution times, and implementing advanced caching patterns.
"""

import functools
import time
import logging
from django.core.cache import cache
from django.conf import settings
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


def cache_performance(cache_name: str) -> Callable:
    """
    Decorator to monitor cache performance and log execution time.
    
    Args:
        cache_name (str): A descriptive name for the cached operation
        
    Returns:
        function: Decorated function that logs execution time
        
    Example:
        @cache_performance("user_list_cache")
        def get_users(request):
            return Response(data)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger.info(f"{cache_name}: {execution_time:.4f}s")
            return result
        return wrapper
    return decorator


def cache_with_timeout(timeout: Optional[int] = None, key_prefix: str = "") -> Callable:
    """
    Decorator to automatically cache function results.
    
    Args:
        timeout (int, optional): Cache timeout in seconds. Uses CACHE_TTL if None.
        key_prefix (str, optional): Prefix for the cache key
        
    Returns:
        function: Decorated function with caching
        
    Example:
        @cache_with_timeout(timeout=600, key_prefix="expensive_")
        def expensive_operation(user_id):
            return expensive_calculation(user_id)
    """
    if timeout is None:
        timeout = settings.CACHE_TTL
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = f"{key_prefix}{func.__name__}_{args}_{kwargs}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache HIT: {cache_key}")
                return cached_result
            
            # Execute function
            logger.info(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        return wrapper
    return decorator


def cache_key_builder(prefix: str, *args, **kwargs) -> str:
    """
    Build a consistent cache key from prefix and arguments.
    
    Args:
        prefix (str): The prefix for the cache key
        *args: Variable positional arguments to include in key
        **kwargs: Variable keyword arguments to include in key
        
    Returns:
        str: Formatted cache key
        
    Example:
        key = cache_key_builder('user', user_id=123, type='profile')
        # Returns: 'user_123_profile'
    """
    parts = [prefix]
    
    # Add positional arguments
    for arg in args:
        parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    for key in sorted(kwargs.keys()):
        parts.append(f"{key}_{kwargs[key]}")
    
    return "_".join(parts)


def clear_cache_pattern(pattern: str) -> int:
    """
    Clear cache entries matching a pattern.
    
    Args:
        pattern (str): Pattern to match (e.g., 'user_*')
        
    Returns:
        int: Number of keys deleted
        
    Example:
        deleted = clear_cache_pattern('user_*')
        print(f"Cleared {deleted} cache entries")
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        
        # Find all keys matching the pattern
        keys = redis_conn.keys(pattern)
        
        # Delete the keys
        if keys:
            deleted_count = redis_conn.delete(*keys)
            logger.info(f"Cleared {deleted_count} cache entries matching '{pattern}'")
            return deleted_count
        
        return 0
    except Exception as e:
        logger.error(f"Error clearing cache pattern '{pattern}': {str(e)}")
        return 0


def get_cache_stats() -> dict:
    """
    Get detailed cache statistics from Redis.
    
    Returns:
        dict: Dictionary containing cache statistics
        
    Example:
        stats = get_cache_stats()
        print(f"Cache memory used: {stats['used_memory_human']}")
    """
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        
        # Get all keys
        keys = redis_conn.keys('*')
        
        # Get Redis info
        info = redis_conn.info()
        
        # Get database stats
        db_stats = redis_conn.info('stats')
        
        return {
            'status': 'success',
            'total_keys': len(keys),
            'used_memory': info.get('used_memory', 0),
            'used_memory_human': info.get('used_memory_human', 'N/A'),
            'used_memory_peak': info.get('used_memory_peak', 0),
            'used_memory_peak_human': info.get('used_memory_peak_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'total_connections_received': db_stats.get('total_connections_received', 0),
            'total_commands_processed': db_stats.get('total_commands_processed', 0),
            'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
            'keys_sample': [k.decode('utf-8') if isinstance(k, bytes) else k for k in keys[:10]],
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }


def warm_cache(data_dict: dict, timeout: Optional[int] = None) -> int:
    """
    Pre-populate cache with data.
    
    Args:
        data_dict (dict): Dictionary of key-value pairs to cache
        timeout (int, optional): Cache timeout in seconds
        
    Returns:
        int: Number of items cached
        
    Example:
        data = {'user_1': user_obj, 'user_2': user_obj2}
        count = warm_cache(data, timeout=3600)
    """
    if timeout is None:
        timeout = settings.CACHE_TTL
    
    count = 0
    try:
        for key, value in data_dict.items():
            cache.set(key, value, timeout=timeout)
            count += 1
        
        logger.info(f"Warmed cache with {count} items")
        return count
    except Exception as e:
        logger.error(f"Error warming cache: {str(e)}")
        return count


class CacheContext:
    """Context manager for cache operations with automatic cleanup."""
    
    def __init__(self, keys_to_clear: list = None):
        """
        Initialize the cache context manager.
        
        Args:
            keys_to_clear (list): List of cache keys to clear on exit
        """
        self.keys_to_clear = keys_to_clear or []
    
    def __enter__(self):
        """Enter the context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and clear specified cache keys."""
        for key in self.keys_to_clear:
            try:
                cache.delete(key)
                logger.info(f"Cleared cache key: {key}")
            except Exception as e:
                logger.error(f"Error clearing cache key {key}: {str(e)}")
        
        return False


def cached_result(timeout: Optional[int] = None) -> Callable:
    """
    Decorator for caching expensive computations.
    
    Args:
        timeout (int, optional): Cache timeout in seconds
        
    Returns:
        function: Decorated function with result caching
        
    Example:
        @cached_result(timeout=300)
        def expensive_query():
            return heavy_computation()
    """
    if timeout is None:
        timeout = settings.CACHE_TTL
    
    def decorator(func: Callable) -> Callable:
        cache_key = f"cached_{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Try cache first
            result = cache.get(cache_key)
            if result is not None:
                logger.info(f"Cache HIT for {cache_key}")
                return result
            
            # Execute and cache
            logger.info(f"Cache MISS for {cache_key}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        
        wrapper.clear_cache = lambda: cache.delete(cache_key)
        return wrapper
    
    return decorator
