from django.test import TestCase

from api.utils.gpt_processor.gpt_settings import get_gpt_processor


class GptSettingsTest(TestCase):
    openai_v1_data = {
        "model": "gpt-4o-mini",
        "usage": {"total_tokens": 20},
        "choices": [{"message": {"content": "Hello, world!"}}]
    }

    openai_v1_normalization = {
        "Company": 'openai',
        "Version": 'v1.0',
        "Model": 'gpt-4o-mini',
        "Token": 20,
        "Result": {
            "model": "gpt-4o-mini",
            "usage": {"total_tokens": 20},
            "choices": [{"message": {"content": "Hello, world!"}}]
        }
    }

    def test_openai_response_normalization_v1_0(self):
        gpt_processor = get_gpt_processor(company="openai")
        result = gpt_processor.process_response(self.openai_v1_data)
        self.assertEqual(result, self.openai_v1_normalization)

    def test_openai_get_content(self):
        gpt_processor = get_gpt_processor(company="openai")
        result = gpt_processor.get_content(self.openai_v1_normalization)
        self.assertEqual(result, "Hello, world!")
