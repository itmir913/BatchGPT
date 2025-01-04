import pandas as pd


def count_rows_in_csv(file):
    try:
        df = pd.read_csv(file)
        return len(df)
    except Exception as e:
        raise Exception(f"Cannot read CSV files: {str(e)}")
