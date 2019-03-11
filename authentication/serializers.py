from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth import authenticate

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


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, allow_blank=False,
                                   help_text="Email required to login")
    password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        email = data.get('email')
        user = authenticate(username=email, password=data.get('password'))
        if user:
            return {
                'email': email,
                'username': user.username,
                'token': user.token
            }
        raise serializers.ValidationError({"error": "Invalid credentials Were Provided"})
