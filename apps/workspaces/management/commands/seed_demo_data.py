from django.core.management.base import BaseCommand

from apps.accounts.models import CustomUser
from apps.tasks.models import Task
from apps.workspaces.models import Workspace, WorkspaceMember


class Command(BaseCommand):
    help = "Seed demo users, workspaces, members, and tasks for frontend manual testing."

    def handle(self, *args, **options):
        manager = self._upsert_user(
            email="manager.demo@workflowx.app",
            password="securepass123",
        )
        member = self._upsert_user(
            email="member.demo@workflowx.app",
            password="securepass123",
        )
        reviewer = self._upsert_user(
            email="member.two@workflowx.app",
            password="securepass123",
        )

        workspace, _ = Workspace.objects.get_or_create(
            workspace_name="Product Launch Workspace",
            defaults={
                "description": "Demo workspace for dashboard, members, and task flow.",
                "created_by": manager,
            },
        )
        if workspace.created_by_id != manager.id:
            workspace.created_by = manager
        workspace.description = "Demo workspace for dashboard, members, and task flow."
        workspace.is_deleted = False
        workspace.save()

        WorkspaceMember.objects.update_or_create(
            workspace=workspace,
            user=manager,
            defaults={"role": "manager"},
        )
        WorkspaceMember.objects.update_or_create(
            workspace=workspace,
            user=member,
            defaults={"role": "member"},
        )
        WorkspaceMember.objects.update_or_create(
            workspace=workspace,
            user=reviewer,
            defaults={"role": "member"},
        )

        self._upsert_task(
            workspace=workspace,
            title="Prepare launch checklist",
            assign_from=manager,
            assign_to=member,
            description="Member can submit this task from the workspace detail screen.",
            status="in_progress",
        )
        self._upsert_task(
            workspace=workspace,
            title="Review release notes",
            assign_from=manager,
            assign_to=reviewer,
            description="Manager can approve or reject this task from in_review state.",
            status="in_review",
        )
        self._upsert_task(
            workspace=workspace,
            title="Publish onboarding guide",
            assign_from=manager,
            assign_to=member,
            description="Completed task used to populate dashboard metrics.",
            status="done",
        )

        side_workspace, _ = Workspace.objects.get_or_create(
            workspace_name="Member Collaboration Hub",
            defaults={
                "description": "Secondary workspace visible to the same member account.",
                "created_by": manager,
            },
        )
        if side_workspace.created_by_id != manager.id:
            side_workspace.created_by = manager
        side_workspace.description = "Secondary workspace visible to the same member account."
        side_workspace.is_deleted = False
        side_workspace.save()

        WorkspaceMember.objects.update_or_create(
            workspace=side_workspace,
            user=manager,
            defaults={"role": "manager"},
        )
        WorkspaceMember.objects.update_or_create(
            workspace=side_workspace,
            user=member,
            defaults={"role": "member"},
        )

        self._upsert_task(
            workspace=side_workspace,
            title="Collect workspace feedback",
            assign_from=manager,
            assign_to=member,
            description="Extra task so the member dashboard shows multiple workspaces.",
            status="in_progress",
        )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("Manager login: manager.demo@workflowx.app / securepass123")
        self.stdout.write("Member login: member.demo@workflowx.app / securepass123")
        self.stdout.write("Second member login: member.two@workflowx.app / securepass123")
        self.stdout.write(f"Primary workspace ID: {workspace.workspace_id}")
        self.stdout.write(f"Secondary workspace ID: {side_workspace.workspace_id}")

    def _upsert_user(self, email, password):
        user, _ = CustomUser.objects.get_or_create(email=email, defaults={"role": "member"})
        user.role = "member"
        user.set_password(password)
        user.save()
        return user

    def _upsert_task(self, workspace, title, assign_from, assign_to, description, status):
        task, _ = Task.objects.get_or_create(
            workspace=workspace,
            title=title,
            defaults={
                "assign_from": assign_from,
                "assign_to": assign_to,
                "description": description,
                "status": status,
            },
        )
        task.assign_from = assign_from
        task.assign_to = assign_to
        task.description = description
        task.status = status
        task.is_deleted = False
        task.save()
        return task
