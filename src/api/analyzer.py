import io
from typing import List


class TextAnalyzer:
    def __init__(self):
        self.fragments: List[str] = []

    def get_fragments(self, sep_regex: str, stream: io.TextIOBase = None, text: str = None):
        pass
