import re
from typing import List


def split_prompt(prompt: str) -> List[str]:
    exclude = [
        "a",
        "an",
        "the",
        "and",
        "or",
        "&&",
        "||",
        "not",
        "is",
        "are",
        "by",
        "on",
        "above",
        "across",
        "after",
        "against",
        "along",
        "among",
        "around",
        "at",
        "before",
        "behind",
        "below",
        "beneath",
        "beside",
        "between",
        "over",
        "under",
        "up",
        "down",
        "off",
        "into",
    ]

    return list(
        filter(
            lambda x: not any((i == x for i in exclude)),
            re.findall(r"([\w\&-]+)", prompt),
        )
    )
