import pytest
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import CustomUser
from apps.tasks.models import Task
from apps.workspaces.models import Workspace, WorkspaceMember


def auth_headers(user):
    token = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


@pytest.fixture
def manager_user():
    return CustomUser.objects.create_user("manager@example.com", "securepass123")


@pytest.fixture
def member_user():
    return CustomUser.objects.create_user("member-task@example.com", "securepass123")


@pytest.fixture
def second_member_user():
    return CustomUser.objects.create_user("member-two@example.com", "securepass123")


@pytest.fixture
def outsider():
    return CustomUser.objects.create_user("outsider-task@example.com", "securepass123")


@pytest.fixture
def workspace(manager_user):
    workspace = Workspace.objects.create(
        workspace_name="Task Workspace",
        description="Task flow",
        created_by=manager_user,
    )
    WorkspaceMember.objects.create(workspace=workspace, user=manager_user, role="manager")
    return workspace


@pytest.fixture
def member_membership(workspace, member_user):
    return WorkspaceMember.objects.create(workspace=workspace, user=member_user, role="member")


@pytest.fixture
def second_member_membership(workspace, second_member_user):
    return WorkspaceMember.objects.create(workspace=workspace, user=second_member_user, role="member")


@pytest.fixture
def assigned_task(workspace, manager_user, member_user, member_membership):
    return Task.objects.create(
        workspace=workspace,
        title="Assigned Task",
        description="Implementation work",
        assign_from=manager_user,
        assign_to=member_user,
    )


class TestTaskCreation:
    @pytest.mark.django_db
    def test_manager_can_create_task_only_inside_workspace_and_assignment_is_optional(self, api_client, workspace, manager_user, member_user, member_membership):
        unassigned_response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/",
            {
                "title": "Draft Task",
                "description": "Create before assigning",
            },
            format="json",
            **auth_headers(manager_user),
        )

        response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/",
            {
                "title": "Implement API",
                "description": "Build the endpoint",
                "assign_to": str(member_user.id),
            },
            format="json",
            **auth_headers(manager_user),
        )

        assert unassigned_response.status_code == status.HTTP_201_CREATED
        assert unassigned_response.data["assign_to"] is None
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "in_progress"
        task = Task.objects.get(id=response.data["id"])
        assert task.assign_from == manager_user
        assert task.assign_to == member_user

    @pytest.mark.django_db
    def test_manager_cannot_assign_task_to_workspace_manager(self, api_client, workspace, manager_user):
        response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/",
            {
                "title": "Invalid assignment",
                "assign_to": str(manager_user.id),
            },
            format="json",
            **auth_headers(manager_user),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "assign_to" in response.data

    @pytest.mark.django_db
    def test_member_cannot_create_task(self, api_client, workspace, member_user, member_membership):
        response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/",
            {"title": "Forbidden", "assign_to": str(member_user.id)},
            format="json",
            **auth_headers(member_user),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_outsider_cannot_create_task(self, api_client, workspace, outsider, member_user, member_membership):
        response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/",
            {"title": "Forbidden", "assign_to": str(member_user.id)},
            format="json",
            **auth_headers(outsider),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestTaskAccessAndManagement:
    @pytest.mark.django_db
    def test_workspace_member_can_list_and_retrieve_tasks(self, api_client, workspace, member_user, member_membership, assigned_task):
        member_user.username = "member-task"
        member_user.save(update_fields=["username"])
        manager = assigned_task.assign_from
        manager.username = "manager-task"
        manager.save(update_fields=["username"])

        list_response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/",
            **auth_headers(member_user),
        )
        detail_response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/",
            **auth_headers(member_user),
        )

        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.data) == 1
        assert list_response.data[0]["assign_to_username"] == "member-task"
        assert detail_response.status_code == status.HTTP_200_OK
        assert detail_response.data["id"] == str(assigned_task.id)
        assert detail_response.data["assign_from_username"] == "manager-task"

    @pytest.mark.django_db
    def test_outsider_cannot_list_or_retrieve_tasks(self, api_client, workspace, outsider, assigned_task):
        list_response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/",
            **auth_headers(outsider),
        )
        detail_response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/",
            **auth_headers(outsider),
        )

        assert list_response.status_code == status.HTTP_403_FORBIDDEN
        assert detail_response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_manager_can_update_task_details_but_not_bypass_status_workflow(self, api_client, workspace, manager_user, second_member_user, second_member_membership, assigned_task):
        response = api_client.put(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/",
            {
                "title": "Reassigned Task",
                "assign_to": str(second_member_user.id),
                "status": "done",
            },
            format="json",
            **auth_headers(manager_user),
        )

        assert response.status_code == status.HTTP_200_OK
        assigned_task.refresh_from_db()
        assert assigned_task.title == "Reassigned Task"
        assert assigned_task.assign_to == second_member_user
        assert assigned_task.status == "in_progress"

    @pytest.mark.django_db
    def test_member_cannot_update_or_delete_task(self, api_client, workspace, member_user, member_membership, assigned_task):
        update_response = api_client.put(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/",
            {"title": "Illegal Update"},
            format="json",
            **auth_headers(member_user),
        )
        delete_response = api_client.delete(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/",
            **auth_headers(member_user),
        )

        assert update_response.status_code == status.HTTP_403_FORBIDDEN
        assert delete_response.status_code == status.HTTP_403_FORBIDDEN


class TestTaskWorkflow:
    @pytest.mark.django_db
    def test_assigned_member_must_upload_submission_before_submit(self, api_client, workspace, member_user, assigned_task):
        response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_review"},
            format="json",
            **auth_headers(member_user),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_assigned_member_submits_task_from_in_progress_to_in_review(self, api_client, workspace, member_user, assigned_task):
        upload_response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/submission/",
            {
                "submission_file": SimpleUploadedFile(
                    "submission.docx",
                    b"demo task content",
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
            **auth_headers(member_user),
        )
        response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_review"},
            format="json",
            **auth_headers(member_user),
        )

        assert upload_response.status_code == status.HTTP_200_OK
        assert response.status_code == status.HTTP_200_OK
        assigned_task.refresh_from_db()
        assert assigned_task.status == "in_review"
        assert assigned_task.submission_file.name.endswith("submission.docx")

    @pytest.mark.django_db
    def test_submission_upload_rejects_invalid_file_type(self, api_client, workspace, member_user, assigned_task):
        response = api_client.post(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/submission/",
            {"submission_file": SimpleUploadedFile("notes.txt", b"invalid", content_type="text/plain")},
            **auth_headers(member_user),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "submission_file" in response.data

    @pytest.mark.django_db
    def test_workspace_member_can_download_submission_file(self, api_client, workspace, manager_user, member_user, assigned_task):
        assigned_task.submission_file = SimpleUploadedFile(
            "submission.docx",
            b"demo task content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        assigned_task.save(update_fields=["submission_file", "updated_at"])

        response = api_client.get(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/submission/download/",
            **auth_headers(manager_user),
        )

        assert response.status_code == status.HTTP_200_OK
        assert "attachment" in response.headers["Content-Disposition"]
        assert "submission.docx" in response.headers["Content-Disposition"]

    @pytest.mark.django_db
    def test_other_member_cannot_submit_task_they_do_not_own(self, api_client, workspace, second_member_user, second_member_membership, assigned_task):
        response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_review"},
            format="json",
            **auth_headers(second_member_user),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_manager_cannot_submit_task_on_behalf_of_member(self, api_client, workspace, manager_user, assigned_task):
        response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_review"},
            format="json",
            **auth_headers(manager_user),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_member_cannot_approve_or_reject_task_in_review(self, api_client, workspace, member_user, assigned_task):
        assigned_task.status = "in_review"
        assigned_task.save(update_fields=["status"])

        approve_response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "done"},
            format="json",
            **auth_headers(member_user),
        )
        reject_response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_progress"},
            format="json",
            **auth_headers(member_user),
        )

        assert approve_response.status_code == status.HTTP_403_FORBIDDEN
        assert reject_response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_manager_can_approve_task_to_done(self, api_client, workspace, manager_user, assigned_task):
        assigned_task.status = "in_review"
        assigned_task.save(update_fields=["status"])

        response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "done"},
            format="json",
            **auth_headers(manager_user),
        )

        assert response.status_code == status.HTTP_200_OK
        assigned_task.refresh_from_db()
        assert assigned_task.status == "done"

    @pytest.mark.django_db
    def test_manager_can_reject_task_back_to_in_progress(self, api_client, workspace, manager_user, assigned_task):
        assigned_task.status = "in_review"
        assigned_task.save(update_fields=["status"])

        response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_progress"},
            format="json",
            **auth_headers(manager_user),
        )

        assert response.status_code == status.HTTP_200_OK
        assigned_task.refresh_from_db()
        assert assigned_task.status == "in_progress"

    @pytest.mark.django_db
    def test_invalid_task_transitions_are_rejected(self, api_client, workspace, member_user, manager_user, assigned_task):
        skip_review = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "done"},
            format="json",
            **auth_headers(member_user),
        )

        assigned_task.status = "done"
        assigned_task.save(update_fields=["status"])
        reopen_done = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_review"},
            format="json",
            **auth_headers(manager_user),
        )

        assert skip_review.status_code == status.HTTP_400_BAD_REQUEST
        assert reopen_done.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_outsider_cannot_change_status(self, api_client, workspace, outsider, assigned_task):
        response = api_client.patch(
            f"/api/v1/workspace/{workspace.workspace_id}/tasks/{assigned_task.id}/status/",
            {"status": "in_review"},
            format="json",
            **auth_headers(outsider),
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
from django.core.files.uploadedfile import SimpleUploadedFile
