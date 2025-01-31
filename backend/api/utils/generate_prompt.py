import logging
import re


def get_prompt(prompt, data):
    try:
        # 데이터의 키를 문자열로 변환 및 공백 제거
        data = {str(key).strip(): str(value).strip() for key, value in data.items()}

        # 중괄호 안의 키 추출
        keys_in_prompt = re.findall(r"{(.+?)}", prompt)

        # 점을 포함한 키를 안전하게 대체
        for key in keys_in_prompt:
            if key in data:
                prompt = prompt.replace(f"{{{key}}}", data[key])
            else:
                # 키가 없는 경우 에러 메시지 반환
                logger = logging.getLogger(__name__)
                logger.log(logging.ERROR, f"API: Missing key: {key} in prompt or data. Data provided: {data}")
                raise ValueError(f"Missing key: {key} in prompt or data. Data provided: {data}")

        return prompt

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.log(logging.ERROR, f"API: An unexpected error occurred when generating prompt: {e}")
        raise ValueError(f"An unexpected error occurred when generating prompt: {e}")
