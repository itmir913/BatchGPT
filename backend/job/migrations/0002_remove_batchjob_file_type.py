# Generated by Django 5.1.4 on 2025-01-05 07:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batchjob',
            name='file_type',
        ),
    ]
