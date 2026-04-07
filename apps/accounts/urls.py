from django.urls import path
from .views import SignUpView, SignInView, SignOutView, UserProfileView, ChangePasswordView, UserDirectoryView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup", SignUpView.as_view(), name="sign-up"),
    path("signin", SignInView.as_view(), name="sign-in"),
    path("signout", SignOutView.as_view(), name="sign-out"),
    path("token/refresh", TokenRefreshView.as_view(), name="refresh-token"),
    path("profile", UserProfileView.as_view(), name="user-profile"),
    path("change-password", ChangePasswordView.as_view(), name="change-password"),
    path("users", UserDirectoryView.as_view(), name="user-directory"),
]
