import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser
from apps.workspaces.models import Workspace, WorkspaceMember


def auth_headers(user):
    token = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


@pytest.fixture
def owner():
    return CustomUser.objects.create_user("owner@example.com", "securepass123")


@pytest.fixture
def member_user():
    return CustomUser.objects.create_user("member@example.com", "securepass123")


@pytest.fixture
def outsider():
    return CustomUser.objects.create_user("outsider@example.com", "securepass123")


@pytest.fixture
def workspace(owner):
    workspace = Workspace.objects.create(
        workspace_name="Core Workspace",
        description="Primary workspace",
        created_by=owner,
    )
    WorkspaceMember.objects.create(workspace=workspace, user=owner, role="manager")
    return workspace


@pytest.fixture
def workspace_member(workspace, member_user):
    return WorkspaceMember.objects.create(
        workspace=workspace,
        user=member_user,
        role="member",
    )


class TestWorkspaceCreation:
    @pytest.mark.django_db
    def test_creator_becomes_workspace_manager(self, api_client, owner):
        response = api_client.post(
            "/api/v1/workspace/",
            {"workspace_name": "New Workspace", "description": "Desc"},
            format="json",
            **auth_headers(owner),
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert WorkspaceMember.objects.filter(
            workspace_id=response.data["workspace_id"],
            user=owner,
            role="manager",
        ).exists()


class TestWorkspaceAccess:
    @pytest.mark.django_db
    def test_member_can_retrieve_workspace(self, api_client, workspace, member_user, workspace_member):
        response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/",
            **auth_headers(member_user),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["workspace_name"] == "Core Workspace"

    @pytest.mark.django_db
    def test_outsider_cannot_retrieve_workspace(self, api_client, workspace, outsider):
        response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/",
            **auth_headers(outsider),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_list_only_returns_joined_workspaces(self, api_client, workspace, owner, outsider):
        another = Workspace.objects.create(
            workspace_name="Another Workspace",
            created_by=outsider,
        )
        WorkspaceMember.objects.create(workspace=another, user=outsider, role="manager")

        response = api_client.get("/api/v1/workspace/", **auth_headers(owner))

        assert response.status_code == status.HTTP_200_OK
        assert [item["workspace_name"] for item in response.data] == ["Core Workspace"]


class TestWorkspaceManagement:
    @pytest.mark.django_db
    def test_manager_can_update_workspace(self, api_client, workspace, owner):
        response = api_client.put(
            f"/api/v1/workspace/{workspace.workspace_id}/",
            {"workspace_name": "Renamed Workspace", "description": workspace.description},
            format="json",
            **auth_headers(owner),
        )

        assert response.status_code == status.HTTP_200_OK
        workspace.refresh_from_db()
        assert workspace.workspace_name == "Renamed Workspace"

    @pytest.mark.django_db
    def test_member_cannot_update_workspace(self, api_client, workspace, member_user, workspace_member):
        response = api_client.put(
            f"/api/v1/workspace/{workspace.workspace_id}/",
            {"workspace_name": "Illegal Rename", "description": workspace.description},
            format="json",
            **auth_headers(member_user),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_manager_can_soft_delete_workspace(self, api_client, workspace, owner):
        response = api_client.delete(
            f"/api/v1/workspace/{workspace.workspace_id}/",
            **auth_headers(owner),
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        workspace.refresh_from_db()
        assert workspace.is_deleted is True


class TestWorkspaceMembers:
    @pytest.mark.django_db
    def test_manager_adds_user_as_member_role(self, api_client, workspace, owner, member_user):
        response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/members/",
            {"user": str(member_user.id), "role": "manager"},
            format="json",
            **auth_headers(owner),
        )

        assert response.status_code == status.HTTP_201_CREATED
        membership = WorkspaceMember.objects.get(workspace=workspace, user=member_user)
        assert membership.role == "member"
        assert response.data["role"] == "member"

    @pytest.mark.django_db
    def test_member_can_list_workspace_members(self, api_client, workspace, member_user, workspace_member):
        response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/members/",
            **auth_headers(member_user),
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    @pytest.mark.django_db
    def test_outsider_cannot_list_workspace_members(self, api_client, workspace, outsider):
        response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/members/",
            **auth_headers(outsider),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_member_cannot_add_or_remove_members(self, api_client, workspace, member_user, workspace_member, outsider):
        add_response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/members/",
            {"user": str(outsider.id)},
            format="json",
            **auth_headers(member_user),
        )

        assert add_response.status_code == status.HTTP_403_FORBIDDEN

        removable = WorkspaceMember.objects.create(workspace=workspace, user=outsider, role="member")
        delete_response = api_client.delete(
            f"/api/v1/workspace/{workspace.workspace_id}/members/{removable.id}/",
            **auth_headers(member_user),
        )

        assert delete_response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_manager_can_remove_member(self, api_client, workspace, owner, member_user, workspace_member):
        response = api_client.delete(
            f"/api/v1/workspace/{workspace.workspace_id}/members/{workspace_member.id}/",
            **auth_headers(owner),
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not WorkspaceMember.objects.filter(id=workspace_member.id).exists()
