from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    description: str
    url: str
    source: str