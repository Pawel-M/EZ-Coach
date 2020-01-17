"""
This module introduces the function that is used to split partial JSONs at the'}{' string.
"""

from typing import Iterable


def split_jsons(json_str: str) -> Iterable[str]:
    """
    Splits the string containing JSON. The input can be a partial JSON object.

    :param json_str: a string containing full or partial JSON object or objects
    :return: an iterable containing strings for each JSON object
    """
    jsons = json_str.split('}{')
    if len(jsons) == 1:
        return json_str,

    jsons[0] = jsons[0] + '}'
    jsons[1:-1] = ['{' + m + '}' for m in jsons[1:-2]]
    jsons[-1] = '{' + jsons[-1]
    return jsons
