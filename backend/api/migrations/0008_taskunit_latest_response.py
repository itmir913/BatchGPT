# Generated by Django 5.1.4 on 2025-01-09 10:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0007_taskunit_task_unit_unit_in_a9db97_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskunit',
            name='latest_response',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='+', to='api.taskunitresponse'),
        ),
    ]
