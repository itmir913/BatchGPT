import hashlib

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from users.models import User


def user_upload_path(instance, filename):
    """사용자 ID별 파일 업로드 경로 설정"""
    """배치 작업을 생성 후 파일 업로드하기"""
    return f"uploads/user_{instance.user.id}/batch_{instance.id}/file_{filename}"


def user_taskunit_path(instance, filename):
    """사용자 ID별 파일 업로드 경로 설정"""
    return f"uploads/user_{instance.user.id}/batch_{instance.batch_job.id}/index_{instance.unit_index}_{filename}"


FILE_TYPES = {
    'CSV': 'csv',
    'PDF': 'pdf',
}


def validate_file_type(file):
    """파일 형식 검증"""
    valid_extensions = FILE_TYPES.values()  # 상수에서 유효 확장자 가져오기
    if not file.name.split('.')[-1].lower() in valid_extensions:
        raise ValidationError(f"Unsupported file type. Only {', '.join(valid_extensions).upper()} files are allowed.")


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        abstract = True


class BatchJob(TimestampedModel):
    """사용자가 생성한 배치 작업"""
    FILE_TYPE_CHOICES = [(key, key) for key in FILE_TYPES.keys()]  # 상수를 기반으로 선택지 생성

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="batch_jobs",
        verbose_name="User"
    )

    file = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=[key for key in FILE_TYPES.keys()])],
        verbose_name="Uploaded File")
    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="File Type"
    )

    class Meta:
        db_table = 'batch_job'  # 테이블 이름 지정
        verbose_name = 'Batch Job'
        verbose_name_plural = 'Batch Jobs'

    def __str__(self):
        return f"BatchJob {self.id} - {self.user.email}"


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
        IN_PROGRESS: [COMPLETED, FAILED],
        COMPLETED: [],
        FAILED: [],
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
        upload_to=user_taskunit_path,
        null=True,
        blank=True,
        verbose_name="File Data"
    )

    status = models.CharField(
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
            models.Index(fields=['status']),  # 상태별 조회 최적화
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
        if not TaskUnitStatus.is_valid_transition(self.status, new_status):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
        self.status = new_status
        self.save()


class Prompt(TimestampedModel):
    """ChatGPT 요청 프롬프트 데이터"""
    text = models.TextField(
        verbose_name="Prompt Text",
        help_text="ChatGPT에 보낸 프롬프트 텍스트"
    )

    hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Prompt Hash",
        help_text="프롬프트 텍스트의 고유 해시값"
    )

    class Meta:
        db_table = 'prompt'
        verbose_name = 'Prompt'
        verbose_name_plural = 'Prompts'

    def __str__(self):
        return f"Prompt {self.id} - {self.text[:50]}"

    @staticmethod
    def generate_hash(text):
        """프롬프트 텍스트의 고유 해시 생성"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @classmethod
    def get_or_create(cls, text):
        """프롬프트를 생성하거나 기존 것을 반환"""
        hash_value = cls.generate_hash(text)
        prompt, created = cls.objects.get_or_create(hash=hash_value, defaults={'text': text})
        return prompt

    """
    prompt_instance = Prompt.get_or_create("Explain AI in simple terms.")
    response = TaskUnitResponse.objects.create(
        task_unit=task_unit_instance,
        prompt=prompt_instance,
        status=TaskUnitStatus.IN_PROGRESS
    )
    """


class TaskUnitResponse(TimestampedModel):
    """TaskUnit에 대한 ChatGPT 응답 저장"""
    task_unit = models.ForeignKey(
        TaskUnit,
        on_delete=models.CASCADE,
        related_name="responses",
        verbose_name="Task Unit"
    )

    prompt = models.ForeignKey(
        Prompt,
        on_delete=models.PROTECT,
        related_name="responses",
        verbose_name="Prompt"
    )

    response_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Response Data",
        help_text="ChatGPT로부터 받은 응답 데이터"
    )

    status = models.CharField(
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
            models.Index(fields=['status']),  # 상태별 조회 최적화
            models.Index(fields=['prompt']),  # 프롬프트별 응답 조회 최적화
        ]

    def __str__(self):
        return f"Response for TaskUnit {self.task_unit.id} - Status: {self.status}"

    def set_status(self, new_status):
        """상태 변경 메서드"""
        if not TaskUnitStatus.is_valid_transition(self.status, new_status):
            raise ValueError(f"Invalid status transition from {self.status} to {new_status}")
        self.status = new_status
        self.save()