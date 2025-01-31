import logging

from api.utils.gpt_processor.openai_gpt_processor import OpenAIGPTProcessor

COMPANY_PROCESSORS = {
    "openai": OpenAIGPTProcessor
}


def get_gpt_processor(*, company=None):
    if not company:
        return None

    processor_class = COMPANY_PROCESSORS.get(company.lower())
    if not processor_class:
        logger = logging.getLogger(__name__)
        logger.log(logging.ERROR, f"API: Unsupported GPT provider.: {company}")
        raise ValueError(f"API: Unsupported GPT provider.: {company}")
    return processor_class()
