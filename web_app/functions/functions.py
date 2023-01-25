import re


def normalize_string(s):
    string = re.sub(r"[^\w\s]", ' ', s)
    string = re.sub(r"\s+", ' ', string)
    normalized_string = string.title().strip()
    return normalized_string
