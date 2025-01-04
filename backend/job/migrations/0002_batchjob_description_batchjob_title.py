# Generated by Django 5.1.4 on 2025-01-04 07:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('job', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchjob',
            name='description',
            field=models.TextField(blank=True, help_text='배치 작업에 대한 설명을 입력하세요. (선택 사항)', null=True,
                                   verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='batchjob',
            name='title',
            field=models.CharField(default='New BatchJob', help_text='배치 작업의 제목을 입력하세요.', max_length=255,
                                   verbose_name='Title'),
        ),
    ]
