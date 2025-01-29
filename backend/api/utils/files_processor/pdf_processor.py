import io
import json
import logging
from enum import Enum

import fitz
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from api.utils.files_processor.file_processor import FileProcessor, ResultType

logger = logging.getLogger(__name__)


class PDFProcessMode(Enum):
    # FILE = "file"
    TEXT = "text"
    IMAGE = "image"
    IMAGE_OCR = "image_ocr"

    # 각 모드의 설명을 매핑
    @classmethod
    def get_descriptions(cls):
        return {
            cls.TEXT.value: "Extract text from the PDF.",
            cls.IMAGE.value: "Extract images from the PDF.",
            cls.IMAGE_OCR.value: "Extract text from the PDF using OCR.",
        }

    @classmethod
    def from_string(cls, value: str):
        mode_map = {mode.value: mode for mode in cls}
        try:
            return mode_map[value]
        except KeyError:
            raise NotImplementedError(f"The given PDF mode '{value}' is not supported in the available modes.")

    @classmethod
    def __contains__(cls, item):
        return item in cls._value2member_map_


class PDFProcessor(FileProcessor):

    def process(self, file, *args, **kwargs):
        try:
            work_unit = kwargs.get('work_unit', 1)
            pdf_mode = kwargs.get('pdf_mode')

            if pdf_mode not in PDFProcessMode:
                raise NotImplementedError(f"Not Implemented PDF mode: {pdf_mode}")

            mode_actions = {
                PDFProcessMode.TEXT: self._extract_text_from_pdf,
            }

            action = mode_actions.get(pdf_mode)
            if not action:
                raise NotImplementedError(f"The given PDF mode '{pdf_mode}' is not supported yet.")

            total_pages = self.get_size(file)
            for start_index in range(0, total_pages, work_unit):
                end_index = min(start_index + work_unit - 1, total_pages - 1)
                yield action(file, start_page=start_index, end_page=end_index)

        except Exception as e:
            logger.log(logging.ERROR, f"API: Unknown error: {str(e)}")
            raise e

    def process_text(self, prompt, *args, **kwargs):
        """파일 텍스트 Prompt 처리 로직"""
        data = kwargs.get('data')
        return f'{prompt}\n\n{data}'

    def _extract_text_from_pdf(self, file, start_page, end_page):
        doc = fitz.open(file)
        all_text = []

        # Ensure the page range is within valid bounds
        start_page = max(0, start_page)
        end_page = min(len(doc) - 1, end_page)

        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]
            all_text.append(page.get_text())

        doc.close()
        return ResultType.TEXT, '\n'.join(all_text)

    def get_size(self, file):
        try:
            if isinstance(file, (InMemoryUploadedFile, TemporaryUploadedFile)):
                file_bytes = io.BytesIO(file.read())
                doc = fitz.open(stream=file_bytes, filetype="pdf")
            else:
                doc = fitz.open(file)

            return len(doc)
        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot read PDF file: {str(e)}")
            raise ValueError(f"Cannot read PDF file: {str(e)}")

    def get_preview(self, file, *args, **kwargs):
        try:
            work_unit = kwargs.get('work_unit', 1)
            pdf_mode = kwargs.get('pdf_mode')
            logger.error(pdf_mode)

            json_data = []
            for index, (_, result) in enumerate(self.process(file, work_unit=work_unit, pdf_mode=pdf_mode)):
                data = {
                    "index": index,
                    "preview": result,  # TODO Result Type에 맞도록 수정해야 함.
                }
                json_data.append(data)
                if index >= 2:  # 3개 제시함
                    break

            return json.dumps(json_data)

        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot read PDF file: {str(e)}")
            raise ValueError(f"Cannot read PDF file: {str(e)}")
