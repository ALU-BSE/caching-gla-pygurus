"""
Django management command to warm up the cache.

This command pre-caches frequently accessed data like user lists and individual users
to improve application performance and reduce database load.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from users.models import User
from users.serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Warm up the cache with frequently accessed data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all caches before warming',
        )

    def handle(self, *args, **options):
        """Execute the cache warming process"""
        try:
            # Optionally clear all caches first
            if options['clear']:
                cache.clear()
                self.stdout.write(
                    self.style.SUCCESS('Cleared all caches')
                )

            # Pre-cache user list
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            cache.set('user_list', serializer.data, timeout=settings.CACHE_TTL)
            self.stdout.write(
                self.style.SUCCESS(f'Cached user list with {len(users)} users')
            )

            # Pre-cache individual users
            cached_count = 0
            for user in users:
                user_data = UserSerializer(user).data
                cache.set(f'user_{user.id}', user_data, timeout=settings.CACHE_TTL)
                cached_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Successfully cached {cached_count} individual users')
            )

            # Summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Cache warming completed!'
                    f'\n  - User list: 1'
                    f'\n  - Individual users: {cached_count}'
                    f'\n  - Total cached items: {cached_count + 1}'
                    f'\n  - Cache TTL: {settings.CACHE_TTL} seconds'
                )
            )

            logger.info(f'Cache warming completed: {cached_count + 1} items cached')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cache warming: {str(e)}')
            )
            logger.error(f'Cache warming failed: {str(e)}')
            raise
