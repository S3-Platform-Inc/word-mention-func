import dataclasses
import datetime

from s3p_sdk.types import S3PDocument


@dataclasses.dataclass
class Event:
    id: int
    document_id: int
    occurred: datetime.datetime
    processed: datetime.datetime | None
    error: str | None
    document: S3PDocument | None = None


@dataclasses.dataclass
class KeywordList:
    id: str
    elements: list[str]

@dataclasses.dataclass
class FoundKeywords:
    list: KeywordList
    elements: dict[str, int]

    def __init__(self, kwlist: KeywordList, elements: dict[str, int]) -> None:
        assert all(element in kwlist.elements for element in elements)
        self.list = kwlist
        self.elements = elements

    def strip(self) -> dict[str, int]:
        return {key: value for key, value in self.elements.items() if value > 0}