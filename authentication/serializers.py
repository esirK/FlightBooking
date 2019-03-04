from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password',]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        User.objects.create_user(**validated_data)
        return validated_data
