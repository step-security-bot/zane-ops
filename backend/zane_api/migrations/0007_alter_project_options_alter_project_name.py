# Generated by Django 5.0.2 on 2024-02-24 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zane_api', '0006_cron_httplog_simplelog_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-updated_at']},
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
