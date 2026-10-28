from dataclasses import dataclass


@dataclass
class SearchResult:
    title: str
    description: str
    url: str
    source: str

@dataclass
class SearchOutcome:
    results: list[SearchResult]
    failed_sources: list[str]
    total_sources: int

    @property
    def all_failed(self) -> bool:
        if self.total_sources == len(self.failed_sources) and self.total_sources > 0:
            return True
        return False