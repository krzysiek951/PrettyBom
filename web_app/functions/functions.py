import re


def normalize_string(s):
    string = re.sub(r"[^\w\s]", ' ', s)
    string = re.sub(r"\s+", ' ', string)
    normalized_string = string.title().strip()
    return normalized_string


def get_number_delimiter(string: str) -> list[str]:
    """Returns all delimiters between numbers."""
    clean_string = string.strip()
    delimiters = list({char for char in clean_string if not char.isdigit()})
    return delimiters
