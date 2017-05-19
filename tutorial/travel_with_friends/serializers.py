from rest_framework import serializers
from travel_with_friends.models import AuthUser, FullTripTable
from django.contrib.auth.models import User
from snippets.models import Snippet
from django.contrib.auth import get_user_model

class FullTripSearchSerializer(serializers.Serializer):
    city = serializers.CharField()
    state = serializers.CharField()
    n_days = serializers.CharField()

class OutsideTripSearchSerializer(serializers.Serializer):
    city = serializers.CharField()
    state = serializers.CharField()
    n_days = serializers.CharField()
    direction = serializers.CharField()

# class UserSerializer(serializers.ModelSerializer):
#     snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=FullTripTable.objects.all())
#     class Meta:
#         model = AuthUser
#         fields = ('id', 'username', 'snippets')
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = get_user_model()
#         fields = ('password', 'username', 'email',)
#         write_only_fields = ('password',)
#         read_only_fields = ('is_staff', 'is_superuser', 'is_active', 'date_joined',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    full_trips = serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    outside_trips = serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    # snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=FullTripTable.objects.all())
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'full_trips', 'outside_trips')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

