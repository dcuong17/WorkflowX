from django.db.models import Count, Q
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import CustomUser
from apps.workspaces.models import Workspace, WorkspaceMember
from apps.workspaces.permissions import IsWorkspaceManager
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend


@extend_schema(tags=["Workspaces"])
class WorkspaceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace_name"]

    def list(self, request):
        workspace_ids = WorkspaceMember.objects.filter(user=request.user).values_list("workspace_id", flat=True)
        workspaces = (
            Workspace.objects.filter(pk__in=workspace_ids, is_deleted=False)
            .distinct()
            .select_related("created_by")
            .prefetch_related("members")
            .annotate(
                total_tasks=Count("tasks", filter=Q(tasks__is_deleted=False)),
                completed_tasks=Count("tasks", filter=Q(tasks__status="done", tasks__is_deleted=False)),
            )
        )
        serializer = self.get_serializer(workspaces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        try:
            workspace = (
                Workspace.objects.filter(is_deleted=False)
                .select_related("created_by")
                .prefetch_related("members")
                .get(pk=pk)
            )
        except Workspace.DoesNotExist:
            raise NotFound("Không có workspace này")
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
        workspace.is_deleted = True
        workspace.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        workspace = serializer.save(created_by=self.request.user)
        WorkspaceMember.objects.create(
            workspace=workspace, user=self.request.user, role="manager"
        )


class WorkspaceMemberViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, workspace_id=None):
        workspace_members = WorkspaceMember.objects.filter(
            workspace=self.kwargs["workspace_id"]
        ).select_related("user")
        from .serializers import WorkspaceMemberSerializer
        serializer = WorkspaceMemberSerializer(workspace_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, workspace_id=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền thêm thành viên")
        serializer = WorkspaceMemberSerializer(data=request.data)
        if serializer.is_valid():
            workspace = Workspace.objects.get(pk=self.kwargs["workspace_id"])
            serializer.save(workspace=workspace, role="member")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, workspace_id=None, pk=None):
        if not IsWorkspaceManager().has_permission(request, self):
            raise PermissionDenied("Chỉ manager mới có quyền xóa thành viên")

        try:
            member = WorkspaceMember.objects.get(
                workspace=self.kwargs["workspace_id"], pk=pk
            )
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại member này")
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
