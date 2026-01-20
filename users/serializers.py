from rest_framework import serializers

from users.models import User, Passenger, Rider


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'user_type']


class PassengerSerializer(serializers.ModelSerializer):
    """Serializer for Passenger model with related user information"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type='passenger'),
        source='user',
        write_only=True
    )
    
    class Meta:
        model = Passenger
        fields = ['id', 'user', 'user_id', 'passenger_id', 'preferred_payment_method', 'home_address']


class RiderSerializer(serializers.ModelSerializer):
    """Serializer for Rider model with related user information"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type='rider'),
        source='user',
        write_only=True
    )
    
    class Meta:
        model = Rider
        fields = ['id', 'user', 'user_id']