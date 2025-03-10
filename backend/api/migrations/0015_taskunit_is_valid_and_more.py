# Generated by Django 5.1.4 on 2025-02-04 10:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0014_auto_20250131_2323'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskunit',
            name='is_valid',
            field=models.BooleanField(default=True, verbose_name='Is Valid'),
        ),
        migrations.AddIndex(
            model_name='taskunit',
            index=models.Index(fields=['is_valid'], name='task_unit_is_vali_5490c2_idx'),
        ),
    ]
