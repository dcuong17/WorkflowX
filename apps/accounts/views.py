from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt import tokens, token_blacklist
from .serializers import SignUpSerializers, SignInSerializers
from .models import CustomUser


# Create your views here.
class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "message": "Đăng ký thành công!",
                },
                status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    def post(self, request):
        serializer = SignInSerializers(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = tokens.RefreshToken.for_user(user)
            return Response(
                {
                    "id": user.id,
                    "email": user.email,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class SignOutView(APIView):
    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh == None:
            return Response(
                {
                    "message": "Token không được để trống",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = tokens.RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response(
                {
                    "message": "Token không hợp lệ",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "message": "Đăng xuất thành công",
            },
            status=status.HTTP_200_OK,
        )
