# Generated by Django 5.1.4 on 2025-01-05 14:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('job', '0002_remove_batchjob_file_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchjob',
            name='file_name',
            field=models.CharField(default='default_filename', max_length=255),
        ),
    ]
