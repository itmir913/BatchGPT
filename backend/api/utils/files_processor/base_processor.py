from abc import ABC, abstractmethod
from enum import Enum


class ResultType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


class BaseFileProcessor(ABC):
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
