from django.db import models
import uuid
from apps.accounts.models import CustomUser


# Create your models here.
class Workspace(models.Model):
    workspace_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workspace_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="workspaces"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WorkspaceMember(models.Model):
    ROLES = [
        ("member", "MEMBER"),
        ("manager", "MANAGER"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    role = models.CharField(max_length=25, choices=ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("workspace", "user")
