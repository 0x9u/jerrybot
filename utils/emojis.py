import re
import math

import emoji

CUSTOM_EMOJI_REGEX = re.compile(r"<a?:\w+:\d+>",  re.IGNORECASE | re.UNICODE)

def get_emoji_multiplier(text: str):
    count = get_emoji_count(text)
    return min(math.sqrt(count), 10)

def detect_emojis(text: str) -> set[str]:
    custom_emojis = CUSTOM_EMOJI_REGEX.findall(text)
    normal_emojis = [char for char in text if emoji.is_emoji(char)]
    return set(custom_emojis + normal_emojis)

def get_emoji_count(text: str) -> int:
    return len(detect_emojis(text))
    