from abc import ABC, abstractmethod


class FileProcessor(ABC):
    @abstractmethod
    def process(self, batch_job_id, file):
        """파일 처리 로직"""
        pass

    @abstractmethod
    def get_size(self, file):
        """파일 크기 반환"""
        pass

    @abstractmethod
    def get_preview(self, file):
        """파일 미리보기 반환"""
        pass
