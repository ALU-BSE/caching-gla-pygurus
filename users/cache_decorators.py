"""
Cache performance monitoring decorators.

This module provides decorators for monitoring cache performance
and logging execution times.
"""

import functools
import time
import logging

logger = logging.getLogger(__name__)


def cache_performance(cache_name):
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
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            logger.info(f"{cache_name}: {execution_time:.4f}s")
            return result
        return wrapper
    return decorator
