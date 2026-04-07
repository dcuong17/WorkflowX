from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate


class SignUpSerializers(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "role", "password", "password_confirm"]
        read_only_fields = ["id", "role"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = CustomUser.objects.create_user(
            email=validated_data.get("email", ""),
            password=validated_data.get("password"),
            username=validated_data.get("username", ""),
        )
        return user

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Mật khẩu xác nhận không khớp"})
        return data

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password quá ngắn")
        return value

    def validate_username(self, value):
        return value.strip()


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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username", "role"]
        read_only_fields = ["id", "role"]

    def validate_email(self, value):
        user = self.instance
        if CustomUser.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Email đã được sử dụng")
        return value

    def validate_username(self, value):
        return value.strip()


class UserDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "username"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Mật khẩu xác nhận không khớp"}
            )
        if len(data["new_password"]) < 8:
            raise serializers.ValidationError(
                {"new_password": "Password quá ngắn"}
            )
        return data

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu cũ không đúng")
        return value
