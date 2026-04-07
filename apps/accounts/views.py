from apps.workspaces.models import WorkspaceMember
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt import tokens, token_blacklist
from .serializers import SignUpSerializers, SignInSerializers, UserProfileSerializer, ChangePasswordSerializer, UserDirectorySerializer
from .models import CustomUser


# Create your views here.
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "user_id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                    "message": "Đăng ký thành công!",
                },
                status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignInSerializers(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = tokens.RefreshToken.for_user(user)
            return Response(
                {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        errors = serializer.errors
        if "non_field_errors" in errors:
            return Response(errors, status=status.HTTP_401_UNAUTHORIZED)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class SignOutView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        refresh = request.data.get("refresh_token")
        if not refresh:
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


class UserProfileView(APIView):
    """Get and update current user profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """Change current user's password."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"message": "Đổi mật khẩu thành công"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDirectoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = CustomUser.objects.all().exclude(id=request.user.id).order_by("username", "email")

        workspace_id = request.query_params.get("workspace_id")
        if workspace_id:
            member_ids = WorkspaceMember.objects.filter(workspace_id=workspace_id).values_list("user_id", flat=True)
            queryset = queryset.exclude(id__in=member_ids)

        serializer = UserDirectorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
