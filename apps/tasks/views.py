from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .serializers import TaskSerializer
from .models import Task, Workspace
from apps.workspaces.models import WorkspaceMember
from apps.workspaces.permissions import IsWorkspaceManager
from rest_framework.exceptions import NotFound, PermissionDenied

ALLOWED_TRANSITIONS = {
    "todo": ["in_progress"],
    "in_progress": ["todo", "review"],
    "review": ["in_progress", "done"],
    "done": ["review"],
}


# Create your views here.


@extend_schema(tags=["Tasks"])
class TaskViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            is_deleted=False, workspace=self.kwargs["workspace_id"]
        ).select_related("assign_to", "assign_from")

    def get_member(self, workspace_id, user):
        try:
            member = WorkspaceMember.objects.get(workspace_id=workspace_id, user=user)
            return member
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại Member này trong workspace")

    def get_manager(self, workspace_id, user):
        try:
            member = WorkspaceMember.objects.get(workspace_id=workspace_id, user=user)
            if member.role != "manager":
                raise PermissionDenied("Không có quyền")
            return member
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại Member này trong workspace")

    def allow_task_members(self, workspace_id):
        return WorkspaceMember.objects.filter(workspace_id=workspace_id).values_list("user_id", flat=True)

    def get_task(self, workspace_id, pk):
        try:
            task = Task.objects.get(workspace=workspace_id, pk=pk, is_deleted=False)
            return task
        except Task.DoesNotExist:
            raise NotFound("Không tồn tại Task này")

    @extend_schema(summary="List all tasks in a workspace")
    def list(self, request, workspace_id=None):
        tasks = self.get_queryset()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Create a new task")
    def create(self, request, workspace_id=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền tạo task")
        serializer = TaskSerializer(
            data=request.data, context={"workspace_id": self.kwargs["workspace_id"]}
        )
        if serializer.is_valid():
            workspace = Workspace.objects.get(pk=self.kwargs["workspace_id"])
            serializer.save(workspace=workspace, assign_from=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, workspace_id=None, pk=None):
        task = self.get_task(self.kwargs["workspace_id"], pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, workspace_id=None, pk=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền chỉnh sửa task")
        task = self.get_task(self.kwargs["workspace_id"], pk)
        serializer = TaskSerializer(task, data=request.data, context={"workspace_id": self.kwargs["workspace_id"]})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, workspace_id=None, pk=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền xóa task")
        task = self.get_task(self.kwargs["workspace_id"], pk)
        task.is_deleted = True
        task.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary="Update task status with transition rules")
    @action(methods=["patch"], detail=True, url_path="status")
    def task_status(self, request, workspace_id=None, pk=None):
        # Any workspace member can update task status
        self.get_member(workspace_id, request.user)
        task = self.get_task(workspace_id, pk)
        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Status required"}, status=status.HTTP_400_BAD_REQUEST)

        allowed = ALLOWED_TRANSITIONS.get(task.status, [])
        if new_status not in allowed:
            return Response(
                {"error": f"Cannot transition from {task.status} to {new_status}. Allowed: {allowed}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        task.status = new_status
        task.save(update_fields=["status", "updated_at"])
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)


# class TaskListView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, workspace_id):
#         tasks = Task.objects.filter(workspace=workspace_id)
#         serializer = TaskSerializer(tasks, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, workspace_id):
#         serializer = TaskSerializer(data=request.data)
#         if serializer.is_valid():
#             workspace = Workspace.objects.get(pk=workspace_id)
#             serializer.save(workspace=workspace, assign_from=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request, workspace_id, pk=None):
        try:
            task = Task.objects.get(workspace_id=workspace_id, pk=pk, is_deleted=False)
            return task
        except Exception:
            raise NotFound("Không có task này")

    def get(self, request, workspace_id, pk=None):
        task = self.get_queryset(request, workspace_id=workspace_id, pk=pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, workspace_id, pk=None):
        task = self.get_queryset(request, workspace_id=workspace_id, pk=pk)
        if task.assign_from != request.user:
            return Response(
                {"message": "Không có quyền chỉnh sửa"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, workspace_id, pk=None):
        task = self.get_queryset(request, workspace_id=workspace_id, pk=pk)
        if task.assign_from != request.user:
            return Response(
                {"message": "Không có quyền xóa"}, status=status.HTTP_403_FORBIDDEN
            )
        task.is_deleted = True
        task.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
