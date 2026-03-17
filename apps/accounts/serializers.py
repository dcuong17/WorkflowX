from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate


class SignUpSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data.get("email", ""),
            password=validated_data.get("password"),
        )
        return user

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password quá ngắn")
        return value


class SignInSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]
        result = authenticate(self.context["request"], email=email, password=password)
        if result:
            return result
        else:
            raise serializers.ValidationError("Sai tên đăng nhập hoặc mật khẩu")
