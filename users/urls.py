from django.urls import path, include
from rest_framework import routers

from users.views import UserViewSet, PassengerViewSet, RiderViewSet, cache_stats

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='user')

# Nested routers for related resources
passengers_router = routers.DefaultRouter()
passengers_router.register(r'', PassengerViewSet, basename='passenger')

riders_router = routers.DefaultRouter()
riders_router.register(r'', RiderViewSet, basename='rider')

urlpatterns = [
    path('cache-stats/', cache_stats, name='cache-stats'),
    path('passengers/', include(passengers_router.urls)),
    path('riders/', include(riders_router.urls)),
] + router.urls