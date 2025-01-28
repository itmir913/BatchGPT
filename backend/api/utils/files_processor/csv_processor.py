import logging
import os
from typing import Generator

import chardet
import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile

from api.utils.files_processor.file_processor import FileProcessor, ResultType
from api.utils.generate_prompt import get_prompt
from backend import settings

CHUNK_SIZE = 1000
DEFAULT_ENCODING = "utf-8"
logger = logging.getLogger(__name__)


class CSVProcessor(FileProcessor):

    def detect_encoding(self, file_path):

        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', DEFAULT_ENCODING)

                if not encoding:
                    logger.log(logging.ERROR,
                               f"API: Encoding detection failed. Using default encoding: {DEFAULT_ENCODING}.")
                    return DEFAULT_ENCODING

                return encoding
        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot detect CSV encoding for file '{file_path}'. "
                                      f"Using default encoding: {DEFAULT_ENCODING}. Error: {e}")
            return DEFAULT_ENCODING

    def process(self, batch_job_id, file) -> Generator[dict, None, None]:
        """
        CSV 파일을 한 행씩 처리하여 반환
        :param batch_job_id:
        :param file: CSV 파일 경로 또는 파일 객체
        :yield: 한 행씩 반환 (dict 형태)
        """
        from api.models import BatchJob

        try:
            batch_job = BatchJob.objects.get(id=batch_job_id)
            prompt = batch_job.configs['prompt']
            selected_headers = batch_job.configs['selected_headers']
            selected_headers = [header.strip() for header in selected_headers]

            if prompt is None or selected_headers is None:
                logger.log(logging.ERROR, f"API: Cannot generate prompts because prompt or selected_headers is None")
                raise ValueError("Cannot generate prompts because prompt or selected_headers is None")

            for chunk in pd.read_csv(file, chunksize=CHUNK_SIZE):
                for row in chunk.itertuples(index=False):
                    filtered = {key.strip(): str(value) for key, value in zip(chunk.columns, row) if
                                key.strip() in selected_headers}
                    yield ResultType.TEXT, get_prompt(prompt, filtered)

        except BatchJob.DoesNotExist as e:
            logger.log(logging.ERROR, f"API: BatchJob.DoesNotExist. {str(e)}")
            raise e
        except Exception as e:
            logger.log(logging.ERROR, f"API: Unknown error: {str(e)}")
            raise e

    def get_size(self, file):
        """
        CSV 파일의 전체 열 개수 반환
        :param file:
        :return:
        """
        try:
            total_rows = 0
            file_path = file if isinstance(file, InMemoryUploadedFile) else os.path.join(settings.BASE_DIR, file.path)

            # 파일을 청크 단위로 읽기
            chunks = pd.read_csv(file_path, encoding=self.detect_encoding(file_path), chunksize=CHUNK_SIZE)
            for chunk in chunks:
                total_rows += len(chunk)

            return total_rows

        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot read CSV files: {str(e)}")
            raise ValueError(f"Cannot read CSV files: {str(e)}")

    def get_preview(self, file):
        """
        CSV 파일의 미리보기 반환(초반 3개 열)
        :param file:
        :return:
        """
        try:
            # 파일을 읽어 3행만 가져오기
            df = pd.read_csv(file, encoding=self.detect_encoding(file), nrows=3)
            df.columns = df.columns.str.strip()
            df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
            return df.to_json(orient='records')

        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot read CSV files: {str(e)}")
            raise ValueError(f"Cannot read CSV files: {str(e)}")
