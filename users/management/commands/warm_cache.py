"""
Django management command to warm up the cache.

This command pre-caches frequently accessed data like user lists, passenger lists,
and rider lists, along with individual records to improve application performance
and reduce database load.
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from users.models import User, Passenger, Rider
from users.serializers import UserSerializer, PassengerSerializer, RiderSerializer
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
            user_count = 0
            for user in users:
                user_data = UserSerializer(user).data
                cache.set(f'user_{user.id}', user_data, timeout=settings.CACHE_TTL)
                user_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Successfully cached {user_count} individual users')
            )

            # Pre-cache passenger list
            passengers = Passenger.objects.all()
            passenger_serializer = PassengerSerializer(passengers, many=True)
            cache.set('passenger_list', passenger_serializer.data, timeout=settings.CACHE_TTL)
            self.stdout.write(
                self.style.SUCCESS(f'Cached passenger list with {len(passengers)} passengers')
            )

            # Pre-cache individual passengers
            passenger_count = 0
            for passenger in passengers:
                passenger_data = PassengerSerializer(passenger).data
                cache.set(f'passenger_{passenger.id}', passenger_data, timeout=settings.CACHE_TTL)
                passenger_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Successfully cached {passenger_count} individual passengers')
            )

            # Pre-cache rider list
            riders = Rider.objects.all()
            rider_serializer = RiderSerializer(riders, many=True)
            cache.set('rider_list', rider_serializer.data, timeout=settings.CACHE_TTL)
            self.stdout.write(
                self.style.SUCCESS(f'Cached rider list with {len(riders)} riders')
            )

            # Pre-cache individual riders
            rider_count = 0
            for rider in riders:
                rider_data = RiderSerializer(rider).data
                cache.set(f'rider_{rider.id}', rider_data, timeout=settings.CACHE_TTL)
                rider_count += 1

            self.stdout.write(
                self.style.SUCCESS(f'Successfully cached {rider_count} individual riders')
            )

            # Summary
            total_items = user_count + passenger_count + rider_count + 3  # +3 for list caches
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Cache warming completed!'
                    f'\n  - User list: 1, Individual users: {user_count}'
                    f'\n  - Passenger list: 1, Individual passengers: {passenger_count}'
                    f'\n  - Rider list: 1, Individual riders: {rider_count}'
                    f'\n  - Total cached items: {total_items}'
                    f'\n  - Cache TTL: {settings.CACHE_TTL} seconds'
                )
            )

            logger.info(f'Cache warming completed: {total_items} items cached')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during cache warming: {str(e)}')
            )
            logger.error(f'Cache warming failed: {str(e)}')
            raise
