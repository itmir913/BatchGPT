def get_prompt(prompt, data):
    """
    :param prompt: "Hello {A}, meet {B}. {A} and {B} are friends."
    :param data: {'A': 'Alice', 'B': 'Bob'}
    :return: Hello Alice, meet Bob. Alice and Bob are friends.
    """
    try:
        # 빈 data 처리
        if not data:
            raise ValueError("Data dictionary is empty.")

        selected_header = list(data.keys())

        # 하나의 키가 있고 포매팅 기호가 없을 때, 값과 템플릿을 \n\n으로 연결
        if len(data) == 1 and not any(f"{{{header}}}" in prompt for header in selected_header):
            # 줄바꿈 두 번 추가
            formatted_prompt = prompt + "\n\n" + ''.join(
                data[header] if data[header] else '' for header in selected_header)
        else:
            # 포매팅 기호가 있는 경우, format_map 사용
            # 빈 값이 있으면 빈 문자열로 대체
            for header in selected_header:
                value = data.get(header, "")
                prompt = prompt.replace(f"{{{header}}}", str(value) if value else '')

            formatted_prompt = prompt

    except KeyError as e:
        raise KeyError("Invalid prompt. Please ensure that all selected columns are present in the prompt."
                       "Columns should be enclosed in curly braces {}.")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}")

    return formatted_prompt
