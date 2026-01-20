from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from django.conf import settings

from users.models import User, Passenger, Rider
from users.serializers import UserSerializer, PassengerSerializer, RiderSerializer
import functools
import time
import logging

logger = logging.getLogger(__name__)


# Cache performance monitoring decorator
def cache_performance(cache_name):
    """Decorator to monitor cache performance and log execution time"""
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


def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys for cache operations"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @cache_performance("user_list_cache")
    def list(self, request, *args, **kwargs):
        """Get list of all users with caching"""
        # Step 1: Create cache key
        cache_key = get_cache_key('user_list')
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        
        # Step 3: Get fresh data from database
        response = super().list(request, *args, **kwargs)
        
        # Step 4: Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response

    @cache_performance("user_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        """Get individual user with caching"""
        user_id = kwargs.get('pk')
        cache_key = get_cache_key('user', user_id)
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        
        # Get fresh data
        response = super().retrieve(request, *args, **kwargs)
        
        # Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response

    def perform_create(self, serializer):
        """Clear relevant caches when creating a new user"""
        # Clear list cache
        cache.delete(get_cache_key('user_list'))
        logger.info("Cleared user_list cache after create")
        
        super().perform_create(serializer)

    def perform_update(self, serializer):
        """Clear both list and individual caches when updating"""
        user_id = serializer.instance.id
        
        # Clear list cache
        cache.delete(get_cache_key('user_list'))
        
        # Clear individual user cache
        cache.delete(get_cache_key('user', user_id))
        
        logger.info(f"Cleared caches for user {user_id} after update")
        
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """Clear caches when deleting a user"""
        user_id = instance.id
        
        # Clear list cache
        cache.delete(get_cache_key('user_list'))
        
        # Clear individual user cache
        cache.delete(get_cache_key('user', user_id))
        
        logger.info(f"Cleared caches for user {user_id} after delete")
        
        super().perform_destroy(instance)


@api_view(['GET'])
def cache_stats(request):
    """View to get cache statistics"""
    try:
        # Get cache info from Redis
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection('default')
        
        # Get all cache keys
        keys = redis_conn.keys('*')
        
        # Get info about cache
        info = redis_conn.info()
        
        return Response({
            'status': 'success',
            'total_keys': len(keys),
            'used_memory': info.get('used_memory_human', 'N/A'),
            'used_memory_peak': info.get('used_memory_peak_human', 'N/A'),
            'connected_clients': info.get('connected_clients', 0),
            'cache_keys': [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys[:20]],  # Limit to first 20
            'message': f'Total cache keys: {len(keys)}'
        })
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


class PassengerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Passengers with caching support.
    
    Implements caching for list and retrieve operations,
    with automatic cache invalidation on create, update, and delete.
    """
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer

    @cache_performance("passenger_list_cache")
    def list(self, request, *args, **kwargs):
        """Get list of all passengers with caching"""
        # Step 1: Create cache key
        cache_key = get_cache_key('passenger_list')
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        
        # Step 3: Get fresh data from database
        response = super().list(request, *args, **kwargs)
        
        # Step 4: Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response

    @cache_performance("passenger_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        """Get individual passenger with caching"""
        passenger_id = kwargs.get('pk')
        cache_key = get_cache_key('passenger', passenger_id)
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        
        # Get fresh data
        response = super().retrieve(request, *args, **kwargs)
        
        # Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response

    def perform_create(self, serializer):
        """Clear relevant caches when creating a new passenger"""
        cache.delete(get_cache_key('passenger_list'))
        logger.info("Cleared passenger_list cache after create")
        
        super().perform_create(serializer)

    def perform_update(self, serializer):
        """Clear both list and individual caches when updating"""
        passenger_id = serializer.instance.id
        
        cache.delete(get_cache_key('passenger_list'))
        cache.delete(get_cache_key('passenger', passenger_id))
        
        logger.info(f"Cleared caches for passenger {passenger_id} after update")
        
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """Clear caches when deleting a passenger"""
        passenger_id = instance.id
        
        cache.delete(get_cache_key('passenger_list'))
        cache.delete(get_cache_key('passenger', passenger_id))
        
        logger.info(f"Cleared caches for passenger {passenger_id} after delete")
        
        super().perform_destroy(instance)


class RiderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Riders with caching support.
    
    Implements caching for list and retrieve operations,
    with automatic cache invalidation on create, update, and delete.
    """
    queryset = Rider.objects.all()
    serializer_class = RiderSerializer

    @cache_performance("rider_list_cache")
    def list(self, request, *args, **kwargs):
        """Get list of all riders with caching"""
        # Step 1: Create cache key
        cache_key = get_cache_key('rider_list')
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        
        # Step 3: Get fresh data from database
        response = super().list(request, *args, **kwargs)
        
        # Step 4: Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response

    @cache_performance("rider_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        """Get individual rider with caching"""
        rider_id = kwargs.get('pk')
        cache_key = get_cache_key('rider', rider_id)
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        
        # Get fresh data
        response = super().retrieve(request, *args, **kwargs)
        
        # Store in cache
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response

    def perform_create(self, serializer):
        """Clear relevant caches when creating a new rider"""
        cache.delete(get_cache_key('rider_list'))
        logger.info("Cleared rider_list cache after create")
        
        super().perform_create(serializer)

    def perform_update(self, serializer):
        """Clear both list and individual caches when updating"""
        rider_id = serializer.instance.id
        
        cache.delete(get_cache_key('rider_list'))
        cache.delete(get_cache_key('rider', rider_id))
        
        logger.info(f"Cleared caches for rider {rider_id} after update")
        
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """Clear caches when deleting a rider"""
        rider_id = instance.id
        
        cache.delete(get_cache_key('rider_list'))
        cache.delete(get_cache_key('rider', rider_id))
        
        logger.info(f"Cleared caches for rider {rider_id} after delete")
        
        super().perform_destroy(instance)