# file_processors.py
import pandas as pd


class CSVProcessor:
    """CSV 파일 처리 클래스"""

    @staticmethod
    def process(file):
        # CSV 파일을 처리하는 로직
        return f"Processed CSV file: {file.name}"

    def get_size(self, file):
        try:
            df = pd.read_csv(file)
            return len(df)
        except Exception as e:
            raise ValueError(f"Cannot read CSV files: {str(e)}")


class PDFProcessor:
    """PDF 파일 처리 클래스"""

    def process(self, file):
        # PDF 파일을 처리하는 로직
        return f"Processed PDF file: {file.name}"
