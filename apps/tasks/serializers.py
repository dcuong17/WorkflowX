from rest_framework import serializers
from django.utils import timezone
from .models import Task
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
            "deadline",
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
        if value is None:
            return value
        workspace_id = self.context.get("workspace_id")
        is_member = WorkspaceMember.objects.filter(
            workspace_id=workspace_id, user=value
        ).exists()
        if not is_member:
            raise serializers.ValidationError("Member không tồn tại trong workspace")
        return value

    def validate_deadline(self, value):
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline không được ở quá khứ")
        return value
