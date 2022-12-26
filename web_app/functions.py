import re
from typing import Optional


def normalize_string(s):
    string = re.sub(r"[^\w\s]", ' ', s)
    string = re.sub(r"\s+", ' ', string)
    normalized_string = string.title().strip()
    return normalized_string


def get_position_delimiter(string: str) -> Optional[str]:
    """" Returns unique non-digit delimiter between numbers. """
    delimiter_candidates = {char for char in string if not char.isdigit()}
    if len(delimiter_candidates) > 1:
        raise ValueError("Only one number delimiter is allowed.")
    if not delimiter_candidates:
        return None
    delimiter = ''.join(delimiter_candidates)
    return delimiter
