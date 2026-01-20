"""
Signal handlers for cache invalidation.

This module implements Django signals to automatically invalidate caches
when User objects are created, updated, or deleted.
"""

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import User
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
