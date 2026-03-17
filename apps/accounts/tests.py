from django.test import TestCase
from rest_framework import status
from .models import CustomUser
import pytest
import conftest


# Create your tests here.
class TestSignup:
    @pytest.mark.django_db
    def test_signup_success(self, api_client):
        data = {"email": "anhcuongtau@gmail.com", "password": "cuong123456"}
        response = api_client.post("/api/v1/auth/signup", data)
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_signup_duplicate_email(self, api_client):
        user = CustomUser.objects.create_user("anhcuongtau@gmail.com", "cuong123")
        data = {"email": "anhcuongtau@gmail.com", "password": "cuong123456"}
        response = api_client.post("/api/v1/auth/signup", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_signup_invalid_email(self, api_client):
        data = {"email": "emailkhonghople", "password": "cuong123456"}
        response = api_client.post("/api/v1/auth/signup", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_signup_short_password(self, api_client):
        data = {"email": "cuong@gmail.com", "password": "123"}
        response = api_client.post("/api/v1/auth/signup", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSignin:
    @pytest.mark.django_db
    def test_signin_success(self, api_client):
        CustomUser.objects.create_user("dinhcuong1703@gmail.com", "cuong2003")
        data = {"email": "dinhcuong1703@gmail.com", "password": "cuong2003"}
        response = api_client.post("/api/v1/auth/signin", data)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_signin_email_unexist(self, api_client):
        data = {"email": "email@gmail.com", "password": "email123"}
        response = api_client.post("/api/v1/auth/signin", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_signin_wrong_password(self, api_client):
        CustomUser.objects.create_user("deptrai@gmail.com", "cuong123")
        data = {"email": "deptrai@gmail.com", "password": "cuong1234"}
        response = api_client.post("/api/v1/auth/signin", data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_signin_invalid_email(self, api_client):
        data = {"email": "cuonggmail.com", "password": "cuong123"}
        response = api_client.post("/api/v1/auth/signin", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_signin_lack_required_field(self, api_client):
        data = {"email": "", "password": ""}
        response = api_client.post("/api/v1/auth/signin", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSignout:
    @pytest.mark.django_db
    def test_signout_success(self, api_client):
        CustomUser.objects.create_user("user@gmail.com", "user123")
        data = {"email": "user@gmail.com", "password": "user123"}
        response = api_client.post("/api/v1/auth/signin", data)
        refresh_token = response.data["refresh_token"]
        signout_response = api_client.post(
            "/api/v1/auth/signout", {"refresh_token": refresh_token}
        )
        print(signout_response.data)
        assert signout_response.status_code == status.HTTP_200_OK

    def test_signout_refresh_token_invalid(self, api_client):
        response = api_client.post(
            "/api/v1/auth/signout", {"refresh_token": "invalidtoken"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_signout_refresh_token_empty(self, api_client):
        response = api_client.post("/api/v1/auth/signout", {"refresh_token": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRefreshToken:
    @pytest.mark.django_db
    def test_refresh_token_success(self, api_client):
        CustomUser.objects.create_user("admin@gmail.com", "admin123")
        data = {"email": "admin@gmail.com", "password": "admin123"}
        response = api_client.post("/api/v1/auth/signin", data)
        refresh_token = response.data["refresh_token"]
        refresh_endpoint = api_client.post(
            "/api/v1/auth/token/refresh", {"refresh": refresh_token}
        )
        assert refresh_endpoint.status_code == status.HTTP_200_OK

    def test_refresh_token_invalid(self, api_client):
        response = api_client.post("/api/v1/auth/token/refresh", {"refresh": "invalid"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_empty(self, api_client):
        response = api_client.post("/api/v1/auth/token/refresh", {"refresh": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
