import logging
import os
from typing import Generator

import pandas as pd
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from api.utils.files_processor.file_processor import FileProcessor, ResultType
from api.utils.generate_prompt import get_prompt
from backend import settings

CHUNK_SIZE = 1000
DEFAULT_ENCODING = "utf-8"
logger = logging.getLogger(__name__)


class CSVProcessor(FileProcessor):

    def process(self, file, *args, **kwargs) -> Generator[dict, None, None]:
        """
        CSV 파일을 한 행씩 처리하여 반환
        :param file: CSV 파일 경로 또는 파일 객체
        :yield: 한 행씩 반환 (dict 형태)
        """
        try:
            for chunk in pd.read_csv(file, chunksize=CHUNK_SIZE):
                for row in chunk.itertuples(index=False):
                    yield ResultType.TEXT, (chunk.columns, row)

            # batch_job = BatchJob.objects.get(id=batch_job_id)
            # prompt = batch_job.configs['prompt']
            # selected_headers = batch_job.configs['selected_headers']
            # selected_headers = [header.strip() for header in selected_headers]
            #
            # if prompt is None or selected_headers is None:
            #     logger.log(logging.ERROR, f"API: Cannot generate prompts because prompt or selected_headers is None")
            #     raise ValueError("Cannot generate prompts because prompt or selected_headers is None")

        except Exception as e:
            logger.log(logging.ERROR, f"API: Unknown error: {str(e)}")
            raise e

    def process_text(self, prompt, *args, **kwargs):
        columns = kwargs.get('columns')
        row = kwargs.get('row')
        selected_headers = kwargs.get('selected_headers')

        filtered = {key.strip(): str(value) for key, value in zip(columns, row) if
                    key.strip() in selected_headers}
        return get_prompt(prompt, filtered)

    def get_size(self, file, *args, **kwargs):
        """
        CSV 파일의 전체 열 개수 반환
        :param file:
        :return:
        """
        try:
            total_rows = 0
            file_path = file if isinstance(file, (InMemoryUploadedFile, TemporaryUploadedFile)) else os.path.join(
                settings.BASE_DIR, file.path)

            # 파일을 청크 단위로 읽기
            chunks = pd.read_csv(file_path, chunksize=CHUNK_SIZE)
            for chunk in chunks:
                total_rows += len(chunk)

            return total_rows

        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot read CSV files: {str(e)}")
            raise ValueError(f"Cannot read CSV files: {str(e)}")

    def get_preview(self, file, *args, **kwargs):
        """
        CSV 파일의 미리보기 반환(초반 3개 열)
        :param file:
        :return:
        """
        try:
            # 파일을 읽어 3행만 가져오기
            # TODO 수정
            df = pd.read_csv(file, nrows=3)
            df.columns = df.columns.str.strip()
            df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)

            final_data = {
                "preview_type": "csv",
                "data": df.to_json(orient='records')
            }

            return final_data

        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot read CSV files: {str(e)}")
            raise ValueError(f"Cannot read CSV files: {str(e)}")
