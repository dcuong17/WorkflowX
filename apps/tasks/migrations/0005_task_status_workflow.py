from django.db import migrations, models


def migrate_task_statuses(apps, schema_editor):
    Task = apps.get_model("tasks", "Task")
    Task.objects.filter(status="todo").update(status="in_progress")
    Task.objects.filter(status="review").update(status="in_review")


def reverse_task_statuses(apps, schema_editor):
    Task = apps.get_model("tasks", "Task")
    Task.objects.filter(status="in_review").update(status="review")


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0004_task_is_deleted_alter_task_status_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_task_statuses, reverse_task_statuses),
        migrations.AlterField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("in_progress", "IN PROGRESS"),
                    ("in_review", "IN REVIEW"),
                    ("done", "DONE"),
                ],
                default="in_progress",
                max_length=20,
            ),
        ),
    ]
