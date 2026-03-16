from rest_framework import serializers
from .models import Task, Workspace
from apps.workspaces.models import WorkspaceMember


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "workspace",
            "title",
            "description",
            "assign_from",
            "assign_to",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "workspace",
            "assign_from",
            "created_at",
            "updated_at",
        ]

    def validate_assign_to(self, value):
        workspace_id = self.context.get("workspace_id")
        is_member = WorkspaceMember.objects.filter(
            workspace_id=workspace_id, user=value
        ).exists()
        if not is_member:
            raise serializers.ValidationError("Member không tồn tại trong workspace")
        return value
