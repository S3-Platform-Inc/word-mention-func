import os
from contextlib import contextmanager
from typing import Generator

from multipledispatch import dispatch

from connection import events, document, event_error, saved_keyword_analysis, event_success
from errors import NotFoundDocument
from static import Event, FoundKeywords


class S3PDatabaseOutbox:

    @dispatch(int)
    def __init__(self, limit: int) -> None:
        self._limit: int = limit
        ...

    @dispatch()
    def __init__(self) -> None:
        if limit := os.getenv("PROC_OUTBOX_LIMIT"):
            self.__init__(int(limit))
        else:
            self.__init__(5)

    def events(self) -> Generator[Event, None, None]:
        for event in events(self._limit):
            try:
                doc = document(event.document_id)
                event.document = doc
                yield event
            except NotFoundDocument as error:
                self.error(event, error.message)

    def error(self, event: Event, message: str) -> None:
        event_error(event.id, message)

    def success(self, event: Event) -> None:
        event_success(event.id)


class S3PDatabaseFunction:

    def __init__(self, outbox: S3PDatabaseOutbox) -> None:
        self._outbox = outbox
        ...

    def save(self, event: Event, kwlist: FoundKeywords, autosave: bool = False) -> None:
        saved_keyword_analysis(event.id, event.document_id, kwlist.list.id, kwlist.strip())
        if autosave:
            self._outbox.success(event)


