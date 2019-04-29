from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

from authentication.models import user_passport
from authentication.serializers import UserSerializer, LoginSerializer
from core.validators import PasswordValidator, validate_email
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        validate_password(password=serializer.validated_data.get('password'),
                          password_validators=[PasswordValidator()])

        # validate_email from django.core.validators could also been have used for this.
        validate_email(serializer.validated_data.get('email'))

        return serializer.save()


class UserLoginAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class PassportPicture(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        passport_photo = str(user.passport_photo)

        return Response(data={"success": {"passport_photo_url": passport_photo}})

    def post(self, request):
        photo = request.FILES.get('passport', None)
        if photo:
            user = request.user
            passport_name = user_passport(user, photo.name)
            user.passport_photo = passport_name
            user.save()
            fs = FileSystemStorage()
            filename = fs.save(passport_name, photo)
            uploaded_file_url = fs.url(filename)

            return Response(data={"success": {"uploaded_file_url": uploaded_file_url}})
        else:
            raise ValidationError("Passport image not supplied")

    def delete(self, request):
        user = request.user
        fs = FileSystemStorage()
        if user.passport_photo:
            fs.delete(name=user.passport_photo)

            user.passport_photo = None
            user.save()
            return Response(data={"message": 'Photo deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        return Response(data={"message": 'user has no photo'}, status=status.HTTP_200_OK)
