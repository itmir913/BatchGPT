from api.utils.files_processor.file_processor import FileProcessor


class PDFProcessor(FileProcessor):
    def process(self, batch_job_id, file, work_unit=1, mode="text"):
        # PDF 파일 처리 로직 구현
        raise NotImplementedError(f"Not Implemented PDF")

    def get_size(self, file):
        # PDF 파일 크기 계산 로직 구현
        raise NotImplementedError(f"Not Implemented PDF")

    def get_preview(self, file):
        # PDF 파일 미리보기 로직 구현
        raise NotImplementedError(f"Not Implemented PDF")
