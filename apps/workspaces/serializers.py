from apps.workspaces.models import Workspace, WorkspaceMember
from rest_framework import serializers


class WorkspaceSerializer(serializers.ModelSerializer):
    total_tasks = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

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
            "created_by_username",
            "total_tasks",
            "completed_tasks",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["workspace_id", "created_by", "created_at", "updated_at", "total_tasks", "completed_tasks"]


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = ["id", "workspace", "user", "user_username", "user_email", "role", "joined_at"]
        read_only_fields = ["id", "workspace", "role", "joined_at"]
