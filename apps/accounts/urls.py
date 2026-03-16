from django.urls import path
from .views import SignUpView, SignInView, SignOutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("signup", SignUpView.as_view(), name="sign-up"),
    path("signin", SignInView.as_view(), name="sign-in"),
    path("signout", SignOutView.as_view(), name="sign-out"),
    path("token/refresh", TokenRefreshView.as_view(), name="refresh-token"),
]
