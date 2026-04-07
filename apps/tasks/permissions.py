from rest_framework.permissions import BasePermission
from apps.workspaces.models import WorkspaceMember
from rest_framework.exceptions import NotFound, PermissionDenied


class IsWorkspaceMember(BasePermission):
    """Allow access only to members of the workspace."""

    def has_permission(self, request, view):
        workspace_id = self._get_workspace_id(view)
        if not workspace_id:
            return True
        if not WorkspaceMember.objects.filter(
            workspace_id=workspace_id, user=request.user
        ).exists():
            raise NotFound("Bạn không phải thành viên workspace này")
        return True

    def _get_workspace_id(self, view):
        return view.kwargs.get("workspace_id") or view.kwargs.get("project_id")


class IsWorkspaceManagerOrAdmin(BasePermission):
    """Only manager or admin roles can write."""

    def has_object_permission(self, request, view, obj):
        workspace_id = self._get_workspace_id(view)
        try:
            member = WorkspaceMember.objects.get(
                workspace_id=workspace_id, user=request.user
            )
            if member.role == "manager":
                return True
            raise PermissionDenied("Không có quyền")
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại Member này trong workspace")

    def has_permission(self, request, view):
        workspace_id = self._get_workspace_id(view)
        if not workspace_id:
            return False  # workspace_id required
        try:
            member = WorkspaceMember.objects.get(
                workspace_id=workspace_id, user=request.user
            )
            return member.role == "manager"
        except WorkspaceMember.DoesNotExist:
            return False

    def _get_workspace_id(self, view):
        return view.kwargs.get("workspace_id") or view.kwargs.get("project_id")
