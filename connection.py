import json
import os

import psycopg2
from s3p_sdk.types import S3PDocument

from static import Event
from errors import NotFoundDocument


def ps_connection():
    """
    Create a connection to the PostgreSQL Control-database by psycopg2
    :return:
    """
    USERNAME = os.getenv('PROC_DB_USER')
    HOST = os.getenv('PROC_DB_HOST')
    PORT = os.getenv('PROC_DB_PORT')
    DATABASE = os.getenv('PROC_DB_NANE')
    PASSWORD = os.getenv('PROC_DB_PASSWORD')

    return psycopg2.connect(
        database=DATABASE,
        user=USERNAME,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )


def events(limit: int) -> tuple[Event, ...]:
    """
    :param limit:
    :return:
    """
    if limit <= 0:
        raise ValueError('Limit must be positive')

    with ps_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select id, doc_id, occurred_on_utc, processed_on_utc, error
                from documents.outbox
                where processed_on_utc is null and error is null
                order by occurred_on_utc
                for update skip locked
                limit %s;
                """,
                (limit,)
            )
            output = cursor.fetchall()
            if output:
                parsed_events = tuple(
                    Event(*row) for row in output
                )
                return parsed_events
            return tuple()


def document(did: int) -> S3PDocument:
    with ps_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select sourceid, id, title, abstract, text, weblink, storagelink, otherdata, published, loaded from documents.document where id = %s limit 1;
                """,
                (did, )
            )
            output = cursor.fetchone()

            if output:
                return S3PDocument(
                    id=output[1],
                    title=output[2],
                    abstract=output[3],
                    text=output[4],
                    link=output[5],
                    storage=output[6],
                    other=output[7],
                    published=output[8],
                    loaded=output[9],
                )

            raise NotFoundDocument(did)

def event_success(event_id: int) -> None:
    """

    :param event_id:
    :return:
    """
    if event_id <= 0:
        raise ValueError("Event ID must be positive")

    try:
        with ps_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    update documents.outbox
                    set processed_on_utc = now()
                    where id = %s;
                    """,
                    (event_id, )
                )
                assert cursor.rowcount > 0
    except psycopg2.Error as e:
        raise psycopg2.DatabaseError(f"Failed to update event {event_id}: {e}")

def event_error(event_id: int, message: str) -> None:
    """

    :param event_id:
    :param message:
    :return:
    """
    if event_id <= 0:
        raise ValueError("Event ID must be positive")

    if not message or not message.strip():
        raise ValueError("Error message cannot be empty")

    try:
        with ps_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    update documents.outbox
                    set error = %s
                    where id = %s;
                    """,
                    (message.strip(), event_id)
                )
                assert cursor.rowcount > 0
    except psycopg2.Error as e:
        raise psycopg2.DatabaseError(f"Failed to update event {event_id}: {e}")


def saved_keyword_analysis(event_id: int, doc_id: int, wordlist_id: str, keywords: dict[str, int]) -> None:
    """

    :param event_id:
    :param doc_id:
    :param wordlist_id:
    :param keywords:
    :return:
    """
    if event_id <= 0:
        raise ValueError("Event ID must be positive")
    if doc_id <= 0:
        raise ValueError("Document ID must be positive")
    if not wordlist_id or not wordlist_id.strip():
        raise ValueError("Wordlist ID cannot be empty")
    if not isinstance(keywords, dict):
        raise ValueError("Keywords must be a dictionary")

    try:
        with ps_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ml.keyword_analysis (document_id, event_id, word_list_id, keywords)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (document_id, event_id, word_list_id)
                        DO UPDATE SET 
                            keywords = EXCLUDED.keywords,
                            analysis_time = CURRENT_TIMESTAMP;
                    """,
                    (doc_id, event_id, wordlist_id.strip(), json.dumps(keywords))
                )
                assert cursor.rowcount > 0
    except psycopg2.Error as e:
                raise psycopg2.DatabaseError(f"Failed to save keyword analysis for document {doc_id}: {e}")

