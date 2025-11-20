from typing import List, Dict, Any, Tuple

class Configuration:
    """
        A small configuration container for user preferences in the IR system.
        Stores two settings:
          - highlight: whether matches should be highlighted using ANSI colors.
          - search_mode: logical mode for combining multiple search terms ("AND" or "OR").
    """
    def __init__(self):
        # Default settings used at program startup.
        self.highlight = True
        self.search_mode = "AND"

    def copy(self):
        """
            Return a *shallow copy* of this configuration object.
            Useful when you want to pass config around without mutating the original.
        """
        copy = Configuration()
        copy.highlight = self.highlight
        copy.search_mode = self.search_mode
        return copy

    def update(self, other: Dict[str, Any]):
        """
            Update this configuration using values from a (loaded) dictionary.
            Only accepts valid keys and types:
              - "highlight": must be a boolean
              - "search_mode": must be "AND" or "OR"

            Invalid entries are silently ignored, ensuring robustness
            against corrupted or manually edited config files.
        """
        if "highlight" in other and isinstance(other["highlight"], bool):
            self.highlight = other["highlight"]

        if "search_mode" in other and other["search_mode"] in ["AND", "OR"]:
            self.search_mode = other["search_mode"]



class Sonnet:
    def __init__(self, sonnet_data: Dict[str, Any]):
        self.title = sonnet_data["title"]
        self.lines = sonnet_data["lines"]


class LineMatch:
    def __init__(self, line_no: int, text: str, spans: List[Tuple[int, int]]):
        self.line_no = line_no
        self.text = text
        self.spans = spans

    def copy(self):
        return LineMatch(self.line_no, self.text, self.spans)

class SearchResult:
    def __init__(self, title: str, title_spans: List[Tuple[int, int]], line_matches: List[LineMatch], matches: int) -> None:
        self.title = title
        self.title_spans = title_spans
        self.line_matches = line_matches
        self.matches = matches

    def copy(self):
        return SearchResult(self.title, self.title_spans, self.line_matches, self.matches)


