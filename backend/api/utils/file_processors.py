# file_processors.py
import logging
import os

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile

from backend import settings


class CSVProcessor:
    """CSV 파일 처리 클래스"""

    @staticmethod
    def process(file):
        # CSV 파일을 처리하는 로직
        return f"Processed CSV file: {file.name}"

    @staticmethod
    def get_size(file):
        try:
            if isinstance(file, InMemoryUploadedFile):
                df = pd.read_csv(file)
            else:
                absolute_file_path = os.path.join(settings.BASE_DIR, file.path)
                df = pd.read_csv(absolute_file_path)
            return len(df)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(str(file))
            raise ValueError(f"Cannot read CSV files: {str(e)}")

    @staticmethod
    def get_preview(file):
        try:
            if isinstance(file, InMemoryUploadedFile):
                df = pd.read_csv(file, nrows=5)
            else:
                absolute_file_path = os.path.join(settings.BASE_DIR, file.path)
                df = pd.read_csv(absolute_file_path, nrows=5)
            return df.to_json(orient='records')
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(str(file))
            raise ValueError(f"Cannot read CSV files: {str(e)}")


class PDFProcessor:
    """PDF 파일 처리 클래스"""

    @staticmethod
    def process(self, file):
        # PDF 파일을 처리하는 로직
        raise NotImplementedError(f"Not Implemented PDF")

    @staticmethod
    def get_size(self, file):
        raise NotImplementedError(f"Not Implemented PDF")

    @staticmethod
    def get_preview(file):
        raise NotImplementedError(f"Not Implemented PDF")
