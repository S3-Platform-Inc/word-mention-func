import logging
import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from multipledispatch import dispatch

from connection import events, document, event_error, saved_keyword_analysis, event_success, healthcheck
from errors import NotFoundDocument
from static import Event, FoundKeywords


class S3PDatabaseOutbox:

    @dispatch(int)
    def __init__(self, limit: int) -> None:
        self._limit: int = limit
        self._log: logging.Logger = logging.getLogger(__name__)

    @dispatch()
    def __init__(self) -> None:
        if limit := os.getenv("PROC_OUTBOX_LIMIT"):
            self.__init__(int(limit))
        else:
            self.__init__(5)

    def health(self) -> None | Exception:
        healthcheck()

    def events(self) -> Generator[Event, None, None]:
        for event in events(self._limit):
            self._log.debug(f"Event {event.id} received")
            try:
                doc = document(event.document_id)
                self._log.debug(f"Document {doc.id} obtain by id: {doc.id}")
                event.document = doc
                self._log.info(f"New event {event.id}, {event.occurred}")
                yield event
            except NotFoundDocument as error:
                self.error(event, error.message)

    def error(self, event: Event, message: str) -> None:
        self._log.warning(f"Event {event.id} down with error: {message}")
        event_error(event.id, message)

    def success(self, event: Event) -> None:
        self._log.info(f"Event {event.id} processing success")
        event_success(event.id)


class S3PDatabaseFunction:

    def __init__(self, outbox: S3PDatabaseOutbox) -> None:
        self._outbox = outbox
        self._log: logging.Logger = logging.getLogger(__name__)

    def save(self, event: Event, kwlist: FoundKeywords, autosave: bool = False) -> None:
        self._log.info(f"Document {event.document.id} was analyzed on kwlist: {kwlist.list.id}")
        saved_keyword_analysis(event.id, event.document_id, kwlist.list.id, kwlist.strip())
        if autosave:
            self._outbox.success(event)


