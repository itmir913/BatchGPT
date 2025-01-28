from abc import ABC, abstractmethod
from enum import IntFlag, auto


class AutoIntFlag(IntFlag):
    def _generate_next_value_(name, start, count, last_values):
        return 1 << count  # 2의 제곱 값 자동 생성


class ResultType(AutoIntFlag):
    TEXT = auto()
    IMAGE = auto()
    FILE = auto()


class FileProcessor(ABC):
    @abstractmethod
    def process(self, file, *args, **kwargs):
        """파일 처리 로직"""
        pass

    @abstractmethod
    def process_text(self, prompt, *args, **kwargs):
        """파일 텍스트 Prompt 처리 로직"""
        pass

    @abstractmethod
    def get_size(self, file, *args, **kwargs):
        """파일 크기 반환"""
        pass

    @abstractmethod
    def get_preview(self, file, *args, **kwargs):
        """파일 미리보기 반환"""
        pass
