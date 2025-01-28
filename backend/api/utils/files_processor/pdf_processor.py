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

        yield action(file, start_page=0, end_page=1)  # 처리 함수 호출

    def _extract_text_from_pdf(self, file, start_page, end_page):
        # text = extract_text_from_pdf("example.pdf", 0, 2)  # Extract text from pages 0 to 2
        doc = fitz.open(file)
        all_text = ""

        # Ensure the page range is within valid bounds
        start_page = max(0, start_page)
        end_page = min(len(doc) - 1, end_page)

        for page_num in range(start_page, end_page + 1):
            page = doc[page_num]
            all_text += page.get_text()  # Extract text from the page

        doc.close()
        return all_text

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

    def get_preview(self, file, work_unit=1):
        # PDF 파일 미리보기 로직 구현
        raise NotImplementedError(f"Not Implemented PDF")
