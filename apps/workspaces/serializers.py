from apps.workspaces.models import Workspace, WorkspaceMember
from rest_framework import serializers


class WorkspaceSerializer(serializers.ModelSerializer):
    total_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()

    def get_total_tasks(self, obj):
        return getattr(obj, "total_tasks", 0)

    def get_completed_tasks(self, obj):
        return getattr(obj, "completed_tasks", 0)

    class Meta:
        model = Workspace
        fields = [
            "workspace_id",
            "workspace_name",
            "description",
            "created_by",
            "total_tasks",
            "completed_tasks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["workspace_id", "created_by", "created_at", "updated_at", "total_tasks", "completed_tasks"]


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMember
        fields = ["id", "workspace", "user", "role", "joined_at"]
        read_only_fields = ["id", "workspace", "role", "joined_at"]
