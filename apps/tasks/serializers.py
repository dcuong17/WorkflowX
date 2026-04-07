from django.utils import timezone
from rest_framework import serializers

from apps.workspaces.models import WorkspaceMember

from .models import Task

ALLOWED_SUBMISSION_EXTENSIONS = {".doc", ".docx", ".xls", ".xlsx"}


class TaskSerializer(serializers.ModelSerializer):
    assign_to_username = serializers.CharField(source="assign_to.username", read_only=True)
    assign_from_username = serializers.CharField(source="assign_from.username", read_only=True)
    submission_file_url = serializers.SerializerMethodField()
    submission_file_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            "id",
            "workspace",
            "title",
            "description",
            "assign_from",
            "assign_from_username",
            "assign_to",
            "assign_to_username",
            "status",
            "deadline",
            "submission_file",
            "submission_file_url",
            "submission_file_name",
            "submitted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "workspace",
            "assign_from",
            "assign_from_username",
            "assign_to_username",
            "status",
            "submitted_at",
            "created_at",
            "updated_at",
        ]

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

    def get_submission_file_url(self, obj):
        if not obj.submission_file:
            return ""
        request = self.context.get("request")
        url = obj.submission_file.url
        return request.build_absolute_uri(url) if request else url

    def get_submission_file_name(self, obj):
        if not obj.submission_file:
            return ""
        return obj.submission_file.name.rsplit("/", 1)[-1]

    def validate_deadline(self, value):
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.utc)
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline không được ở quá khứ")
        return value

    def validate_submission_file(self, value):
        if value in (None, ""):
            return value

        lower_name = value.name.lower()
        if not any(lower_name.endswith(ext) for ext in ALLOWED_SUBMISSION_EXTENSIONS):
            raise serializers.ValidationError("Chỉ cho phép file Word hoặc Excel")
        return value
