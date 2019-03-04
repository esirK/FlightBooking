from django.contrib.auth import get_user_model
from rest_framework import generics

from authentication.serializers import UserSerializer
from core.validators import PasswordValidator, validate_email
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationAPIView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        validate_password(password=serializer.validated_data.get('password'),
                          password_validators=[PasswordValidator()])

        # validate_email from django.core.validators could also been have used for this.
        validate_email(serializer.validated_data.get('email'))

        return serializer.save()
