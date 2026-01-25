"""
Signal handlers for cache invalidation.

This module implements Django signals to automatically invalidate caches
when User, Passenger, or Rider objects are created, updated, or deleted.
"""

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User, Passenger, Rider
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, created, **kwargs):
    """
    Signal handler to invalidate user cache when a user is saved.
    
    This handles both creation and updates of User objects,
    ensuring that cached user list and individual user data are cleared.
    """
    # Always clear the user list cache
    cache.delete('user_list')
    
    # Clear individual user cache if updating existing user
    if not created:
        cache.delete(f'user_{instance.id}')
    
    action = "created" if created else "updated"
    logger.info(f"Cache invalidated for user {instance.id} ({action})")


@receiver(post_delete, sender=User)
def invalidate_user_cache_on_delete(sender, instance, **kwargs):
    """
    Signal handler to invalidate user cache when a user is deleted.
    
    Clears the user list cache and the individual user cache.
    """
    # Clear the user list cache
    cache.delete('user_list')
    
    # Clear individual user cache
    cache.delete(f'user_{instance.id}')
    
    logger.info(f"Cache invalidated for deleted user {instance.id}")


@receiver(post_save, sender=Passenger)
def invalidate_passenger_cache(sender, instance, created, **kwargs):
    """
    Signal handler to invalidate passenger cache when a passenger is saved.
    
    This handles both creation and updates of Passenger objects,
    ensuring that cached passenger list and individual passenger data are cleared.
    """
    # Always clear the passenger list cache
    cache.delete('passenger_list')
    
    # Clear individual passenger cache if updating existing passenger
    if not created:
        cache.delete(f'passenger_{instance.id}')
    
    action = "created" if created else "updated"
    logger.info(f"Cache invalidated for passenger {instance.id} ({action})")


@receiver(post_delete, sender=Passenger)
def invalidate_passenger_cache_on_delete(sender, instance, **kwargs):
    """
    Signal handler to invalidate passenger cache when a passenger is deleted.
    
    Clears the passenger list cache and the individual passenger cache.
    """
    # Clear the passenger list cache
    cache.delete('passenger_list')
    
    # Clear individual passenger cache
    cache.delete(f'passenger_{instance.id}')
    
    logger.info(f"Cache invalidated for deleted passenger {instance.id}")


@receiver(post_save, sender=Rider)
def invalidate_rider_cache(sender, instance, created, **kwargs):
    """
    Signal handler to invalidate rider cache when a rider is saved.
    
    This handles both creation and updates of Rider objects,
    ensuring that cached rider list and individual rider data are cleared.
    """
    # Always clear the rider list cache
    cache.delete('rider_list')
    
    # Clear individual rider cache if updating existing rider
    if not created:
        cache.delete(f'rider_{instance.id}')
    
    action = "created" if created else "updated"
    logger.info(f"Cache invalidated for rider {instance.id} ({action})")


@receiver(post_delete, sender=Rider)
def invalidate_rider_cache_on_delete(sender, instance, **kwargs):
    """
    Signal handler to invalidate rider cache when a rider is deleted.
    
    Clears the rider list cache and the individual rider cache.
    """
    # Clear the rider list cache
    cache.delete('rider_list')
    
    # Clear individual rider cache
    cache.delete(f'rider_{instance.id}')
    
    logger.info(f"Cache invalidated for deleted rider {instance.id}")
