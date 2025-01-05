# file_settings.py
from api.utils.file_processors import CSVProcessor, PDFProcessor


class FileSettings:
    """파일 관련 설정과 처리 로직을 관리하는 클래스"""

    # 파일 타입 설정
    FILE_TYPES = {
        'CSV': 'csv',
        'PDF': 'pdf',
    }

    FILE_TYPE_CHOICES = [(key, key) for key in FILE_TYPES.keys()]  # 상수를 기반으로 선택지 생성

    # 파일 처리 클래스 매핑
    FILE_PROCESSORS = {
        'csv': CSVProcessor,
        'pdf': PDFProcessor,
    }

    # 업로드 경로 설정
    @staticmethod
    def get_upload_path(instance, filename):
        """사용자 ID별 파일 업로드 경로 설정"""
        return f"uploads/user_{instance.user.id}/batch_{instance.id}/file_{filename}"

    @staticmethod
    def get_taskunit_path(instance, filename):
        """사용자 ID별 파일 업로드 경로 설정"""
        return f"uploads/user_{instance.user.id}/batch_{instance.batch_job.id}/index_{instance.unit_index}_{filename}"

    @staticmethod
    def get_file_extension(file_name):
        return file_name.split('.')[-1].lower()

    # 파일 확장자 검증
    @staticmethod
    def is_valid_extension(file_name):
        """파일 확장자 검사"""
        valid_extensions = list(FileSettings.FILE_TYPES.values())
        file_extension = FileSettings.get_file_extension(file_name)
        return file_extension in valid_extensions

    # 파일 처리 함수 (다형성 적용)
    @staticmethod
    def process_file(file_type, file):
        """파일 타입에 따라 파일 처리 로직을 실행"""
        processor_class = FileSettings.FILE_PROCESSORS.get(file_type.lower())
        if processor_class:
            processor = processor_class()  # 클래스를 바로 인스턴스화
            return processor.process(file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def get_total_size_for_file_types(file):
        file_type = FileSettings.get_file_extension(file.name)
        processor_class = FileSettings.FILE_PROCESSORS.get(file_type.lower())
        if processor_class:
            processor = processor_class()  # 클래스를 바로 인스턴스화
            try:
                size = processor.get_size(file)
                return size
            except ValueError as e:
                raise ValueError(f"Unsupported file: {str(e)}")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
