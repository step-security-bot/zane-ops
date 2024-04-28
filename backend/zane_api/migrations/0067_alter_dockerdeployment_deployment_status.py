# Generated by Django 5.0.2 on 2024-04-25 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zane_api", "0066_alter_dockerdeployment_image_tag"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dockerdeployment",
            name="deployment_status",
            field=models.CharField(
                choices=[
                    ("QUEUED", "Queued"),
                    ("STARTING", "Starting"),
                    ("RESTARTING", "Restarting"),
                    ("CANCELLED", "Cancelled"),
                    ("HEALTHY", "Healthy"),
                    ("UNHEALTHY", "Unhealthy"),
                    ("OFFLINE", "Offline"),
                ],
                default="QUEUED",
                max_length=10,
            ),
        ),
    ]
