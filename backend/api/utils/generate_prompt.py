def get_prompt(prompt, data):
    try:
        selected_header = list(data.keys())

        # 하나의 키가 있고 포매팅 기호가 없을 때, 값과 템플릿을 \n\n으로 연결
        if len(data) == 1 and not any(f"{{{header}}}" in prompt for header in selected_header):
            # 줄바꿈 두 번 추가
            formatted_prompt = prompt + "\n\n" + ''.join(data[header] for header in selected_header)
        else:
            # 포매팅 기호가 있는 경우, format_map 사용
            formatted_prompt = prompt.format_map(data)

        return formatted_prompt

    except KeyError as e:
        return f"{prompt}\n\n{str(data)}"
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}")


def get_openai_result(response_data):
    return response_data.get('choices',
                             [])[0].get('message', {}).get('content', None) \
        if response_data is not None else None
