"""
Utility functions.
"""
from typing import List

def _handle_str(string_param: str) -> List[str]:
    if isinstance(string_param, str):
        return [string_param]
    return string_param
