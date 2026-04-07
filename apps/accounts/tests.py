import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser


def auth_headers(user):
    token = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class TestSignup:
    @pytest.mark.django_db
    def test_signup_success_requires_matching_password_confirmation(self, api_client):
        payload = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "password_confirm": "securepass123",
        }

        response = api_client.post("/api/v1/auth/signup", payload)

        assert response.status_code == status.HTTP_201_CREATED
        user = CustomUser.objects.get(email="newuser@example.com")
        assert response.data["role"] == "member"
        assert user.role == "member"

    @pytest.mark.django_db
    def test_signup_rejects_mismatched_password_confirmation(self, api_client):
        payload = {
            "email": "mismatch@example.com",
            "password": "securepass123",
            "password_confirm": "differentpass123",
        }

        response = api_client.post("/api/v1/auth/signup", payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data


class TestSignin:
    @pytest.mark.django_db
    def test_signin_returns_default_system_role(self, api_client):
        user = CustomUser.objects.create_user("signin@example.com", "securepass123")

        response = api_client.post(
            "/api/v1/auth/signin",
            {"email": user.email, "password": "securepass123"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == "member"
        assert "access_token" in response.data


class TestUserProfile:
    @pytest.mark.django_db
    def test_get_profile_returns_role_and_email(self, api_client):
        user = CustomUser.objects.create_user("profile@example.com", "securepass123")

        response = api_client.get("/api/v1/auth/profile", **auth_headers(user))

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": str(user.id),
            "email": "profile@example.com",
            "role": "member",
        }

    @pytest.mark.django_db
    def test_update_profile_can_change_email_but_not_role(self, api_client):
        user = CustomUser.objects.create_user("before@example.com", "securepass123")

        response = api_client.put(
            "/api/v1/auth/profile",
            {"email": "after@example.com", "role": "admin"},
            format="json",
            **auth_headers(user),
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == "after@example.com"
        assert user.role == "member"
        assert response.data["role"] == "member"


class TestChangePassword:
    @pytest.mark.django_db
    def test_change_password_success(self, api_client):
        user = CustomUser.objects.create_user("password@example.com", "oldpass123")

        response = api_client.post(
            "/api/v1/auth/change-password",
            {
                "old_password": "oldpass123",
                "new_password": "newpass1234",
                "new_password_confirm": "newpass1234",
            },
            format="json",
            **auth_headers(user),
        )

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("newpass1234")

    @pytest.mark.django_db
    def test_change_password_rejects_wrong_old_password(self, api_client):
        user = CustomUser.objects.create_user("wrongold@example.com", "oldpass123")

        response = api_client.post(
            "/api/v1/auth/change-password",
            {
                "old_password": "bad-old-pass",
                "new_password": "newpass1234",
                "new_password_confirm": "newpass1234",
            },
            format="json",
            **auth_headers(user),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
