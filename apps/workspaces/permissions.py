from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import WorkspaceMember


class IsWorkspaceManager(BasePermission):
    """Allow access only to users with manager role in the given workspace."""

    message = "Chỉ manager mới có quyền thực hiện thao tác này"

    def has_permission(self, request, view):
        workspace_id = self._get_workspace_id(request, view)
        if workspace_id is None:
            return False
        try:
            member = WorkspaceMember.objects.get(workspace_id=workspace_id, user=request.user)
            if member.role != "manager":
                self.message = "Chỉ manager mới có quyền thực hiện thao tác này"
                return False
            return True
        except WorkspaceMember.DoesNotExist:
            raise NotFound("Không tồn tại Member này trong workspace")

    def _get_workspace_id(self, request, view):
        # Check common URL param names
        for key in ("workspace_id", "pk"):
            value = view.kwargs.get(key)
            if value is not None:
                return value
        return None
