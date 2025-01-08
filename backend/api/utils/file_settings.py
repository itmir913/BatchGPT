import hashlib
import os

from api.utils.files_processor.csv_processor import CSVProcessor
from api.utils.files_processor.pdf_processor import PDFProcessor


class FileSettings:
    """파일 관련 설정과 처리 로직을 관리하는 클래스"""

    # 파일 타입 설정
    FILE_TYPES = {
        'CSV': 'csv',
        'PDF': 'pdf',
    }

    # 파일 처리 클래스 매핑
    FILE_PROCESSORS = {
        'csv': CSVProcessor,
        'pdf': PDFProcessor,
    }

    FILE_TYPE_CHOICES = [(key, key) for key in FILE_TYPES.keys()]  # 상수를 기반으로 선택지 생성

    @staticmethod
    def get_upload_path(instance, filename):
        """사용자 ID별 파일 업로드 경로 설정"""
        name, ext = os.path.splitext(filename)
        hashed_name = hashlib.sha256(name.encode('utf-8')).hexdigest()

        return f"uploads/user_{instance.user.id}/batch_{instance.id}/{hashed_name}{ext}"

    @staticmethod
    def get_taskunit_path(instance, filename):
        """사용자 ID별 파일 업로드 경로 설정"""
        name, ext = os.path.splitext(filename)
        hashed_name = hashlib.sha256(name.encode('utf-8')).hexdigest()

        return f"uploads/user_{instance.user.id}/batch_{instance.batch_job.id}/index_{instance.unit_index}_{hashed_name}{ext}"

    @staticmethod
    def get_file_extension(file_name):
        """파일 확장자 추출"""
        return file_name.split('.')[-1].lower()

    @staticmethod
    def is_valid_extension(file_name):
        """파일 확장자 검사"""
        return FileSettings.get_file_extension(file_name) in FileSettings.FILE_TYPES.values()

    @staticmethod
    def process(file_type, file):
        """파일 타입에 따라 파일 처리 로직을 실행"""
        processor_class = FileSettings.FILE_PROCESSORS.get(file_type.lower())
        if not processor_class:
            raise ValueError(f"Unsupported file type: {file_type}")
        return processor_class().process(file)

    @staticmethod
    def handle_file_processor_method(file, method):
        """파일 처리 메서드 공통 처리"""
        file_type = FileSettings.get_file_extension(file.name)
        processor_class = FileSettings.FILE_PROCESSORS.get(file_type.lower())
        if not processor_class:
            raise ValueError(f"Unsupported file type: {file_type}")

        try:
            processor = processor_class()
            return getattr(processor, method)(file)
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")

    @staticmethod
    def get_size(file):
        return FileSettings.handle_file_processor_method(file, 'get_size')

    @staticmethod
    def get_preview(file):
        return FileSettings.handle_file_processor_method(file, 'get_preview')
