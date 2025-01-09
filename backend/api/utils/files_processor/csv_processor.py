import logging
import os
from typing import Generator

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile

from api.utils.files_processor.file_processor import FileProcessor
from api.utils.generate_prompt import get_prompt
from backend import settings

CHUNK_SIZE = 1000


class CSVProcessor(FileProcessor):

    def process(self, batch_job_id, file, work_unit=1) -> Generator[dict, None, None]:
        """
        CSV 파일을 한 행씩 처리하여 반환
        :param work_unit:
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
                raise ValueError("Cannot generate prompts because prompt or selected_headers is None")

            for chunk in pd.read_csv(file, chunksize=1):  # 한 행씩 읽음
                for _, row in chunk.iterrows():
                    filtered = {key.strip(): str(value) for key, value in row.to_dict().items() if
                                key.strip() in selected_headers}
                    yield get_prompt(prompt, filtered)

        except BatchJob.DoesNotExist as e:
            raise e
        except Exception as e:
            raise e

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
        # TODO 리팩토링 대상

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
