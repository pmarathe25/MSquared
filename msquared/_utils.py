"""
Utility functions.
"""

def _handle_str(string_param):
    if isinstance(string_param, str):
        return [string_param]
    return string_param
