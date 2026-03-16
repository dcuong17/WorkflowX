from apps.workspaces.models import Workspace, WorkspaceMember
from rest_framework import serializers


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = [
            "workspace_id",
            "workspace_name",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["workspace_id", "created_by", "created_at", "updated_at"]


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMember
        fields = ["id", "workspace", "user", "role", "joined_at"]
        read_only_fields = ["id", "workspace", "role", "joined_at"]
