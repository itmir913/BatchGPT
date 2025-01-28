from enum import Enum

from api.utils.files_processor.file_processor import FileProcessor


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
            ProcessMode.TEXT: self._process_text,
        }

        action = mode_actions.get(mode)
        if not action:
            raise ValueError(f"Unexpected mode: {mode}")

        yield action(batch_job_id, file, work_unit)  # 처리 함수 호출

        raise NotImplementedError(f"Not Implemented PDF")

    def _process_text(self, batch_job_id, file, work_unit):
        yield "Processing in TEXT mode"

    def get_size(self, file):
        # PDF 파일 크기 계산 로직 구현
        raise NotImplementedError(f"Not Implemented PDF")

    def get_preview(self, file, work_unit=1):
        # PDF 파일 미리보기 로직 구현
        raise NotImplementedError(f"Not Implemented PDF")
