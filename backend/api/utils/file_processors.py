# file_processors.py
import logging
import os

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile

from backend import settings

CHUNK_SIZE = 1000


class CSVProcessor:
    """CSV 파일 처리 클래스"""

    @staticmethod
    def process(file):
        # CSV 파일을 처리하는 로직
        return f"Processed CSV file: {file.name}"

    @staticmethod
    def get_size(file):
        logger = logging.getLogger(__name__)

        try:
            total_rows = 0

            # 파일 경로 설정
            if isinstance(file, InMemoryUploadedFile):
                file_path = file  # InMemoryUploadedFile은 경로가 필요 없으므로 그대로 사용
            else:
                file_path = os.path.join(settings.BASE_DIR, file.path)

            # 파일을 청크 단위로 읽기
            chunks = pd.read_csv(file_path, chunksize=CHUNK_SIZE)
            for chunk in chunks:
                total_rows += len(chunk)

            return total_rows

        except Exception as e:
            logger.error(f"Error reading file: {str(file)}")
            raise ValueError(f"Cannot read CSV files: {str(e)}")

    @staticmethod
    def get_preview(file):
        logger = logging.getLogger(__name__)

        try:

            # 파일 경로 설정
            if isinstance(file, InMemoryUploadedFile):
                file_path = file  # InMemoryUploadedFile은 경로가 필요 없으므로 그대로 사용
            else:
                file_path = os.path.join(settings.BASE_DIR, file.path)

            # 파일을 읽어 5행만 가져오기
            df = pd.read_csv(file_path, nrows=5)

            return df.to_json(orient='records')

        except Exception as e:
            logger.error(f"Error reading file: {str(file)}")
            raise ValueError(f"Cannot read CSV files: {str(e)}")


class PDFProcessor:
    """PDF 파일 처리 클래스"""

    @staticmethod
    def process(file):
        # PDF 파일을 처리하는 로직
        raise NotImplementedError(f"Not Implemented PDF")

    @staticmethod
    def get_size(file):
        raise NotImplementedError(f"Not Implemented PDF")

    @staticmethod
    def get_preview(file):
        raise NotImplementedError(f"Not Implemented PDF")
