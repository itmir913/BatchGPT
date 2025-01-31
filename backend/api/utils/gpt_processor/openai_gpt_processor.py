import logging
from typing import Dict, Any

from api.utils.gpt_processor.base_gpt_processor import BaseGPTProcessor, format_response


def normalize_v1_0(data: Dict[str, Any]) -> Dict[str, Any]:
    version = 'v1.0'
    model = data.get('model', None)
    total_tokens = data.get('usage', {}).get('total_tokens', 0)
    content = data.get('choices',
                       [])[0].get('message', {}).get('content', None)

    return {
        'model': model,
        'total_tokens': total_tokens,
        'content': content,
        'normalize_version': version,
    }


class OpenAIGPTProcessor(BaseGPTProcessor):
    COMPANY = 'openai'
    LATEST_VERSION = 'v1.0'
    VERSION_FUNCTIONS = {
        "v1.0": normalize_v1_0,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_response(self, result):
        processor_method = OpenAIGPTProcessor.VERSION_FUNCTIONS.get(self.LATEST_VERSION)
        if not processor_method:
            self.log_error(f"API: Unsupported version: {self.LATEST_VERSION}")
            raise ValueError(f"Unsupported version: {self.LATEST_VERSION}")

        normalize = processor_method(result)

        return format_response(result=result, company=self.COMPANY, version=normalize.get('normalize_version'),
                               model=normalize.get('model'), token=normalize.get('total_tokens'))

    def get_content(self, data):
        version = data.get("Version", None)
        response = data.get("Result", None)

        processor_method = OpenAIGPTProcessor.VERSION_FUNCTIONS.get(version.lower())
        if not processor_method:
            self.log_error(f"API: Unsupported OpenAI Json Version: {version}")
            raise ValueError(f"Unsupported OpenAI Json Version: {version}")

        if not response:
            self.log_error(f"API: OpenAI No Response.")
            raise ValueError(f"OpenAI No Response.")

        return processor_method(response).get('content')

    def log_error(self, message):
        self.logger.log(logging.ERROR, message)
