from django.db import models
from apps.accounts.models import CustomUser
from apps.workspaces.models import Workspace
import uuid


# Create your models here.
class Task(models.Model):

    STATUS = [
        ("todo", "TODO"),
        ("in_progress", "IN PROGRESS"),
        ("done", "DONE"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    assign_from = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_from_tasks",
    )
    assign_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_to_tasks",
    )
    status = models.CharField(max_length=20, choices=STATUS, default="todo")
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
