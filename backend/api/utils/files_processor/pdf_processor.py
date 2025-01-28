import io
import logging
from enum import Enum

import fitz
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

from api.utils.files_processor.file_processor import FileProcessor

logger = logging.getLogger(__name__)


class ProcessMode(Enum):
    TEXT = "text"
    # FILE = "file"
    # IMAGE = "image"
    # IMAGE_OCR = "image_ocr"


class PDFProcessor(FileProcessor):

    def process(self, batch_job_id, file, work_unit=1, mode=ProcessMode.TEXT):
        if mode not in ProcessMode:
            raise NotImplementedError(f"Not Implemented PDF mode: {mode}")

        mode_actions = {
            ProcessMode.TEXT: self._extract_text_from_pdf,
        }

        action = mode_actions.get(mode)
        if not action:
            raise ValueError(f"Unexpected mode: {mode}")

        total_pages = self.get_size(file)
        for start_index in range(0, total_pages, work_unit):
            end_index = min(start_index + work_unit - 1, total_pages - 1)
            yield action(file, start_page=start_index, end_page=end_index)

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
        return '\n'.join(all_text)

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

    def get_preview(self, file, work_unit=1, mode=ProcessMode.TEXT):
        try:
            json_data = []
            for index, result in enumerate(self.process(0, file, work_unit, mode)):
                data = {
                    "index": index,
                    "result": result
                }
                json_data.append(data)
                if index >= 1:
                    break

            return json_data

        except Exception as e:
            logger.log(logging.ERROR, f"API: Cannot read PDF file: {str(e)}")
            raise ValueError(f"Cannot read PDF file: {str(e)}")
