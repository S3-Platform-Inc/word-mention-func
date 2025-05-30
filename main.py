import logging
import os
import time

from dotenv import load_dotenv

from config import kw_load
from errors import NotFoundDocument
from word_mention import check_words_from_list

# Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Вывод в stdout (cmd)
    ]
)
logger = logging.getLogger(__name__)
logger.info("Word-mention-func start & check environment")

# load .env
load_dotenv()
logger.debug(".env loaded")

from connector import S3PDatabaseOutbox, S3PDatabaseFunction

# DB connect
outbox = S3PDatabaseOutbox(5)
func = S3PDatabaseFunction(outbox)

outbox.health()
logger.debug(f"Database is healthy")


# Keywords
kws = kw_load()
logger.debug("keyword lists loaded")

logger.info("Main loop start")
while True:
    try:
        for event in outbox.events():
            if not isinstance(event.document.text, str):
                outbox.error(event, "text field is not a string")
                logger.warning(f"text field is not a string in document ({event.document.id})")
                continue

            for kw in kws:
                fk = check_words_from_list(text=event.document.text, word_list=kw)
                func.save(event, fk)
            outbox.success(event)
    except NotFoundDocument as error:
        logger.debug(f"Main loop sleep to {os.getenv("PROC_LOOP_DELAY")}")
        time.sleep(int(os.getenv("PROC_LOOP_DELAY")))
