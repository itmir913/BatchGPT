import logging
import os

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile

from api.utils.files_processor.file_processor import FileProcessor
from backend import settings

CHUNK_SIZE = 1000


class CSVProcessor(FileProcessor):

    def process(self, file):
        # CSV 파일 처리 로직 구현
        return f"Processed CSV file: {file.name}"
        pass

    def get_size(self, file):
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

    def get_preview(self, file):
        logger = logging.getLogger(__name__)

        try:

            # 파일 경로 설정
            if isinstance(file, InMemoryUploadedFile):
                file_path = file  # InMemoryUploadedFile은 경로가 필요 없으므로 그대로 사용
            else:
                file_path = os.path.join(settings.BASE_DIR, file.path)

            # 파일을 읽어 3행만 가져오기
            df = pd.read_csv(file_path, nrows=3)
            df.columns = df.columns.str.strip()
            df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
            return df.to_json(orient='records')

        except Exception as e:
            logger.error(f"Error reading file: {str(file)}")
            raise ValueError(f"Cannot read CSV files: {str(e)}")
