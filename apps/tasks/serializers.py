from django.utils import timezone
from rest_framework import serializers

from apps.workspaces.models import WorkspaceMember

from .models import Task


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
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        assign_to = attrs.get("assign_to")
        if self.instance is None and assign_to is None:
            raise serializers.ValidationError(
                {"assign_to": "Task phải được giao cho một member trong workspace"}
            )
        return attrs

    def validate_assign_to(self, value):
        if value is None:
            return value

        workspace_id = self.context.get("workspace_id")
        try:
            membership = WorkspaceMember.objects.get(
                workspace_id=workspace_id,
                user=value,
            )
        except WorkspaceMember.DoesNotExist:
            raise serializers.ValidationError("Member không tồn tại trong workspace")

        if membership.role != "member":
            raise serializers.ValidationError("Task chỉ có thể giao cho member trong workspace")
        return value

    def validate_deadline(self, value):
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline không được ở quá khứ")
        return value
