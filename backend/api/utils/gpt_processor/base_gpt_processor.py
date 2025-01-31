from abc import ABC, abstractmethod


def format_response(*, result=None, company=None, version=None, model=None, token=None):
    return {
        "Company": company,
        "Version": version,
        "Model": model if model is not None else result.get('model'),
        "Token": token if token is not None else result.get('total_tokens'),
        "Result": result,
    }


class BaseGPTProcessor(ABC):
    @abstractmethod
    def process_response(self, result):
        pass

    @abstractmethod
    def get_content(self, data):
        pass
