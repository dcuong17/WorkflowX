from rest_framework import status
from django.http import FileResponse
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from drf_spectacular.utils import extend_schema

from apps.workspaces.models import WorkspaceMember
from apps.workspaces.permissions import IsWorkspaceManager

from .models import Task, Workspace
from .serializers import TaskSerializer, submission_file_exists

ALLOWED_TRANSITIONS = {
    "in_progress": ["in_review"],
    "in_review": ["in_progress", "done"],
    "done": [],
}


@extend_schema(tags=["Tasks"])
class TaskViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_queryset(self):
        return Task.objects.filter(
            is_deleted=False,
            workspace=self.kwargs["workspace_id"],
            workspace__is_deleted=False,
        ).select_related("assign_to", "assign_from")

    def get_workspace(self, workspace_id):
        try:
            return Workspace.objects.get(pk=workspace_id, is_deleted=False)
        except Workspace.DoesNotExist:
            raise NotFound("Workspace không tồn tại")

    def ensure_workspace_member(self, workspace_id, user):
        self.get_workspace(workspace_id)
        try:
            return WorkspaceMember.objects.get(workspace_id=workspace_id, user=user)
        except WorkspaceMember.DoesNotExist:
            raise PermissionDenied("Không có quyền truy cập workspace này")

    def get_task(self, workspace_id, pk):
        try:
            return Task.objects.get(
                workspace=workspace_id,
                workspace__is_deleted=False,
                pk=pk,
                is_deleted=False,
            )
        except Task.DoesNotExist:
            raise NotFound("Không tồn tại task này")

    @extend_schema(summary="List all tasks in a workspace")
    def list(self, request, workspace_id=None):
        self.ensure_workspace_member(workspace_id, request.user)
        serializer = TaskSerializer(self.get_queryset(), many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Create a new task")
    def create(self, request, workspace_id=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền tạo task")

        serializer = TaskSerializer(
            data=request.data,
            context={"workspace_id": self.kwargs["workspace_id"], "request": request},
        )
        if serializer.is_valid():
            workspace = self.get_workspace(self.kwargs["workspace_id"])
            serializer.save(workspace=workspace, assign_from=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, workspace_id=None, pk=None):
        self.ensure_workspace_member(workspace_id, request.user)
        task = self.get_task(workspace_id, pk)
        return Response(TaskSerializer(task, context={"request": request}).data, status=status.HTTP_200_OK)

    def update(self, request, workspace_id=None, pk=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền chỉnh sửa task")

        task = self.get_task(workspace_id, pk)
        serializer = TaskSerializer(
            task,
            data=request.data,
            partial=True,
            context={"workspace_id": self.kwargs["workspace_id"], "request": request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, workspace_id=None, pk=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền xóa task")

        task = self.get_task(workspace_id, pk)
        task.is_deleted = True
        task.save(update_fields=["is_deleted", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary="Move task through submission and review workflow")
    @action(methods=["patch"], detail=True, url_path="status")
    def task_status(self, request, workspace_id=None, pk=None):
        member = self.ensure_workspace_member(workspace_id, request.user)
        task = self.get_task(workspace_id, pk)
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "Status required"}, status=status.HTTP_400_BAD_REQUEST)

        allowed = ALLOWED_TRANSITIONS.get(task.status, [])
        if new_status not in allowed:
            return Response(
                {
                    "error": (
                        f"Cannot transition from {task.status} to {new_status}. "
                        f"Allowed: {allowed}"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if task.assign_to_id is None:
            raise PermissionDenied("Task này chưa được giao cho member nào")

        if task.status == "in_progress" and new_status == "in_review":
            if member.role != "member":
                raise PermissionDenied("Chỉ member được giao task mới có quyền nộp bài")
            if task.assign_to_id != request.user.id:
                raise PermissionDenied("Chỉ người được giao task mới có quyền nộp bài")
            if not task.submission_file:
                raise PermissionDenied("Member phải tải lên file Word hoặc Excel trước khi nộp bài")
            task.submitted_at = timezone.now()

        if task.status == "in_review" and new_status in {"done", "in_progress"}:
            if member.role != "manager":
                raise PermissionDenied("Chỉ manager mới có quyền duyệt hoặc từ chối task")
            if new_status == "in_progress":
                task.submitted_at = None

        task.status = new_status
        task.save(update_fields=["status", "submitted_at", "updated_at"])
        return Response(TaskSerializer(task, context={"request": request}).data, status=status.HTTP_200_OK)

    @extend_schema(summary="Upload task submission file")
    @action(methods=["post"], detail=True, url_path="submission")
    def submission(self, request, workspace_id=None, pk=None):
        member = self.ensure_workspace_member(workspace_id, request.user)
        task = self.get_task(workspace_id, pk)

        if member.role != "member":
            raise PermissionDenied("Chỉ member được giao task mới có thể tải file lên")
        if task.assign_to_id != request.user.id:
            raise PermissionDenied("Chỉ người được giao task mới có thể tải file lên")

        serializer = TaskSerializer(
            task,
            data={"submission_file": request.data.get("submission_file")},
            partial=True,
            context={"workspace_id": self.kwargs["workspace_id"], "request": request},
        )
        if serializer.is_valid():
            serializer.save(submitted_at=None)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Download task submission file")
    @action(methods=["get"], detail=True, url_path="submission/download")
    def download_submission(self, request, workspace_id=None, pk=None):
        self.ensure_workspace_member(workspace_id, request.user)
        task = self.get_task(workspace_id, pk)

        if not submission_file_exists(task):
            raise NotFound("Task này chưa có file nộp bài")

        try:
            task.submission_file.open("rb")
        except FileNotFoundError as exc:
            raise NotFound("File đã không còn tồn tại trên máy chủ, vui lòng tải lên lại") from exc

        return FileResponse(
            task.submission_file,
            as_attachment=True,
            filename=task.submission_file.name.rsplit("/", 1)[-1],
        )
