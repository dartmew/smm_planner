import re


def format_text(text):
    formatted_text = text.replace('-', '—')
    formatted_text = formatted_text.strip()
    formatted_text = re.sub(r'\s+', ' ', formatted_text)
    formatted_text = re.sub(r'\s+([.,!?:;])', r'\1', formatted_text)
    formatted_text = re.sub(r'([.,!?:;])([^\s])', r'\1 \2', formatted_text)
    formatted_text = re.sub(r'\s*—\s*', ' — ', formatted_text)
    formatted_text = re.sub(r'(^|\s)"\s+', r'\1"', formatted_text)
    formatted_text = re.sub(r'\s+"(\s|$)', r'"\1', formatted_text)
    formatted_text = re.sub(r'(^|\s)\'\s+', r'\1\'', formatted_text)
    formatted_text = re.sub(r'\s+\'(\s|$)', r'\'\1', formatted_text)
    formatted_text = _format_quotes(formatted_text)

    return formatted_text


def _format_quotes(text):
    quotes = ['"', "'"]
    result = []

    for i, char in enumerate(text):
        if char in quotes:
            if i == 0:
                result.append('«')
            elif i == len(text) - 1:
                result.append('»')
            else:
                if text[i - 1] == ' ':
                    result.append('«')
                elif text[i + 1] == ' ':
                    result.append('»')
        else:
            result.append(char)

    return ''.join(result)
