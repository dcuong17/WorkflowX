from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from apps.workspaces.models import Workspace, WorkspaceMember
from apps.workspaces.permissions import IsWorkspaceManager
from .serializers import WorkspaceMemberSerializer, WorkspaceSerializer


@extend_schema(tags=["Workspaces"])
class WorkspaceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace_name"]

    def _annotated_queryset(self):
        return (
            Workspace.objects.filter(is_deleted=False)
            .select_related("created_by")
            .prefetch_related("members")
            .annotate(
                total_tasks=Count("tasks", filter=Q(tasks__is_deleted=False)),
                completed_tasks=Count(
                    "tasks",
                    filter=Q(tasks__status="done", tasks__is_deleted=False),
                ),
            )
        )

    def list(self, request):
        workspace_ids = WorkspaceMember.objects.filter(user=request.user).values_list("workspace_id", flat=True)
        workspaces = self._annotated_queryset().filter(pk__in=workspace_ids).distinct()
        serializer = self.get_serializer(workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            workspace = self._annotated_queryset().get(pk=pk)
        except Workspace.DoesNotExist:
            raise NotFound("Workspace không tồn tại")
        is_member = WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists()
        if not is_member:
            raise PermissionDenied("Không có quyền truy cập workspace này")
        serializer = self.get_serializer(workspace)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền chỉnh sửa workspace")
        return super().update(request, pk)

    def destroy(self, request, pk):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền xóa workspace")

        workspace = self.get_object()
        workspace.tasks.filter(is_deleted=False).update(
            is_deleted=True,
            updated_at=timezone.now(),
        )
        workspace.is_deleted = True
        workspace.save(update_fields=["is_deleted", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        workspace = serializer.save(created_by=self.request.user)
        WorkspaceMember.objects.create(
            workspace=workspace,
            user=self.request.user,
            role="manager",
        )


class WorkspaceMemberViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_active_workspace(self, workspace_id):
        try:
            return Workspace.objects.get(pk=workspace_id, is_deleted=False)
        except Workspace.DoesNotExist:
            raise NotFound("Workspace không tồn tại")

    def _ensure_workspace_member(self, user, workspace_id):
        self._get_active_workspace(workspace_id)
        if not WorkspaceMember.objects.filter(
            workspace_id=workspace_id,
            user=user,
        ).exists():
            raise PermissionDenied("Không có quyền truy cập workspace này")

    def list(self, request, workspace_id=None):
        self._ensure_workspace_member(request.user, self.kwargs["workspace_id"])
        workspace_members = WorkspaceMember.objects.filter(
            workspace=self.kwargs["workspace_id"]
        ).select_related("user")
        serializer = WorkspaceMemberSerializer(workspace_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, workspace_id=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền thêm thành viên")
        serializer = WorkspaceMemberSerializer(data=request.data)
        if serializer.is_valid():
            workspace = self._get_active_workspace(self.kwargs["workspace_id"])
            serializer.save(workspace=workspace, role="member")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, workspace_id=None, pk=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền xóa thành viên")

        self._get_active_workspace(self.kwargs["workspace_id"])
        try:
            member = WorkspaceMember.objects.get(
                workspace=self.kwargs["workspace_id"],
                pk=pk,
            )
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại thành viên này")
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
