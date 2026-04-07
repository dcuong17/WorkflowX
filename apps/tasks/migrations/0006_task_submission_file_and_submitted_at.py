from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tasks", "0005_task_status_workflow"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="submission_file",
            field=models.FileField(blank=True, null=True, upload_to="task_submissions/"),
        ),
        migrations.AddField(
            model_name="task",
            name="submitted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
