import os

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from api.utils.file_settings import FileSettings
from users.models import User


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        abstract = True


class BatchJobStatus:
    """BatchJob의 상태와 전환 규칙 관리"""
    CREATED = 'CREATED'
    UPLOADED = 'UPLOADED'
    CONFIGS = 'CONFIGS'
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

    CHOICES = [
        (CREATED, 'Created'),
        (UPLOADED, 'Uploaded'),
        (CONFIGS, 'Configs'),
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    VALID_TRANSITIONS = {
        CREATED: [UPLOADED],
        UPLOADED: [UPLOADED, CONFIGS],
        CONFIGS: [UPLOADED, CONFIGS, PENDING, IN_PROGRESS],
        PENDING: [IN_PROGRESS, PENDING],
        IN_PROGRESS: [IN_PROGRESS, COMPLETED, FAILED],
        COMPLETED: [IN_PROGRESS, COMPLETED],
        FAILED: [IN_PROGRESS, FAILED],
    }

    @classmethod
    def is_valid_transition(cls, current_status, new_status):
        """상태 전환이 유효한지 확인"""
        return new_status in cls.VALID_TRANSITIONS.get(current_status, [])


class BatchJob(TimestampedModel):
    """사용자가 생성한 배치 작업"""

    """사용자 키"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="batch_jobs",
        verbose_name="User"
    )

    """배치 작업 기본 설명(제목, 설명)"""
    title = models.CharField(
        max_length=255,
        verbose_name="Title",
        default="New BatchJob",
        help_text="배치 작업의 제목을 입력하세요."
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="배치 작업에 대한 설명을 입력하세요. (선택 사항)"
    )

    """업로드한 파일 설정"""
    file = models.FileField(
        upload_to=FileSettings.get_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=[key for key in FileSettings.FILE_TYPES.keys()])],
        verbose_name="Uploaded File")

    file_name = models.CharField(
        max_length=255,
        blank=True,
        null=True)

    """배치 작업 기본 설정"""
    configs = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Configurations for BatchJob"
    )

    """BatchJob 상태 관리"""
    batch_job_status = models.CharField(
        max_length=20,
        choices=BatchJobStatus.CHOICES,
        default=BatchJobStatus.CREATED,
        verbose_name="Status"
    )

    class Meta:
        """테이블 설정"""
        db_table = 'batch_job'  # 테이블 이름 지정
        verbose_name = 'Batch Job'
        verbose_name_plural = 'Batch Jobs'

    def __str__(self):
        return f"BatchJob {self.id} - {self.user.email}"

    def set_status(self, new_status):
        """상태 변경 메서드"""
        if not BatchJobStatus.is_valid_transition(self.batch_job_status, new_status):
            raise ValueError(f"Invalid status transition from {self.batch_job_status} to {new_status}")
        self.batch_job_status = new_status

    def clean(self):
        """유효성 검사: 파일 확장자 확인"""
        if self.file and not FileSettings.is_valid_extension(self.file.name):
            raise ValidationError(f"Unsupported file type: {self.file.name}."
                                  f"Only {', '.join(FileSettings.FILE_TYPES.values()).upper()} files are allowed.")

    def delete_old_file(self):
        """기존 파일 삭제"""
        if self.pk:
            try:
                old_instance = BatchJob.objects.get(pk=self.pk)
                if old_instance.file and old_instance.file != self.file:
                    if os.path.isfile(old_instance.file.path):
                        os.remove(old_instance.file.path)
            except BatchJob.DoesNotExist:
                pass

    def delete(self, *args, **kwargs):
        """객체 삭제 시 파일도 삭제"""
        try:
            if self.file and os.path.isfile(self.file.path):
                self.file.delete()
        except Exception as e:
            pass

        super().delete(*args, **kwargs)  # 부모 클래스의 delete 호출

    def save(self, *args, **kwargs):
        """기존 파일 삭제 -> 유효성 검사 -> 새 파일 저장"""
        self.delete_old_file()
        self.clean()
        super().save(*args, **kwargs)

    def _process_file_method(self, method_name):
        """파일 타입에 맞는 처리 로직을 실행하는 공통 메서드"""
        if not self.file:
            raise ValueError("File type not defined for processing.")

        method_map = {
            'process': FileSettings.process,
            'get_total_size': FileSettings.get_size,
            'get_preview': FileSettings.get_preview
        }

        method = method_map.get(method_name)
        if not method:
            raise ValueError(f"Unsupported method: {method_name}")

        return method(self.file)

    def process(self):
        """파일 타입에 맞는 처리 로직 실행"""
        return self._process_file_method('process')

    def get_size(self):
        """파일 타입에 맞는 Total Size 로직 실행"""
        return self._process_file_method('get_total_size')

    def get_preview(self):
        """파일 타입에 맞는 Preview 로직 실행"""
        return self._process_file_method('get_preview')


class TaskUnitStatus:
    """TaskUnit의 상태와 전환 규칙 관리"""
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

    CHOICES = [
        (PENDING, 'Pending'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    VALID_TRANSITIONS = {
        PENDING: [IN_PROGRESS, FAILED],
        IN_PROGRESS: [IN_PROGRESS, COMPLETED, FAILED],
        COMPLETED: [PENDING],
        FAILED: [PENDING, IN_PROGRESS],
    }

    @classmethod
    def is_valid_transition(cls, current_status, new_status):
        """상태 전환이 유효한지 확인"""
        return new_status in cls.VALID_TRANSITIONS.get(current_status, [])


class TaskUnit(TimestampedModel):
    """배치 작업의 개별 작업 단위"""
    batch_job = models.ForeignKey(
        BatchJob,
        on_delete=models.CASCADE,
        related_name='task_units',
        verbose_name="Batch Job"
    )

    unit_index = models.IntegerField(verbose_name="Unit Index")  # 작업 단위 순서 (CSV 행 번호 or PDF 페이지 묶음)

    text_data = models.TextField(
        null=True,
        blank=True,
        verbose_name="Text Data")  # CSV 행 데이터
    file_data = models.FileField(
        upload_to=FileSettings.get_taskunit_path,
        null=True,
        blank=True,
        verbose_name="File Data"
    )

    task_unit_status = models.CharField(
        max_length=20,
        choices=TaskUnitStatus.CHOICES,
        default=TaskUnitStatus.PENDING,
        verbose_name="Status"
    )

    class Meta:
        db_table = 'task_unit'
        verbose_name = 'Task Unit'
        verbose_name_plural = 'Task Units'
        indexes = [
            models.Index(fields=['batch_job']),  # 배치 작업별 조회 최적화
            models.Index(fields=['task_unit_status']),  # 상태별 조회 최적화
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['batch_job', 'unit_index'],
                name='unique_task_unit_per_batch'
            )
        ]

    def __str__(self):
        return f"TaskUnit {self.unit_index} - BatchJob {self.batch_job.id}"

    def set_status(self, new_status):
        """상태 변경 메서드"""
        if not TaskUnitStatus.is_valid_transition(self.task_unit_status, new_status):
            raise ValueError(f"Invalid status transition from {self.task_unit_status} to {new_status}")
        self.task_unit_status = new_status


# @receiver(post_save, sender=TaskUnit)
# def start_celery_task(sender, instance, created, **kwargs):
#     if created:
#         process_task_unit.delay(instance.id)


# TODO TaskUnitResponse가 삭제될 때, 남아있는 Prompt를 어떻게 할 것인지 고려해야 함.
class TaskUnitResponse(TimestampedModel):
    """TaskUnit에 대한 ChatGPT 응답 저장"""
    task_unit = models.ForeignKey(
        TaskUnit,
        on_delete=models.CASCADE,  # TODO SET_NULL을 고민할 것.
        related_name="responses",
        verbose_name="Task Unit"
    )

    request_data = models.TextField(
        null=True,
        blank=True,
        verbose_name="Prompt Data per TaskUnit"
    )

    response_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Response Data",
        help_text="ChatGPT로부터 받은 응답 데이터"
    )

    task_response_status = models.CharField(
        max_length=20,
        choices=TaskUnitStatus.CHOICES,
        default=TaskUnitStatus.PENDING,
        verbose_name="Status"
    )

    error_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Error Code",
        help_text="요청 실패 시 발생한 오류 코드"
    )

    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="Error Message",
        help_text="요청 실패 시 발생한 오류 메시지"
    )

    processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Processing Time",
        help_text="요청 처리 시간 (초 단위)"
    )

    class Meta:
        db_table = 'task_unit_response'
        verbose_name = 'Task Unit Response'
        verbose_name_plural = 'Task Unit Responses'
        ordering = ['task_unit', 'created_at']
        indexes = [
            models.Index(fields=['task_unit']),  # 작업 단위별 응답 조회 최적화
            models.Index(fields=['task_response_status']),  # 상태별 조회 최적화
        ]

    def __str__(self):
        return f"Response for TaskUnit {self.task_unit.id} - Status: {self.task_response_status}"

    def set_status(self, new_status):
        """상태 변경 메서드"""
        if not TaskUnitStatus.is_valid_transition(self.task_response_status, new_status):
            raise ValueError(f"Invalid status transition from {self.task_response_status} to {new_status}")
        self.task_response_status = new_status
        self.save()
