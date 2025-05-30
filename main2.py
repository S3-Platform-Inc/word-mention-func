import time
from traceback import print_tb

from dotenv import load_dotenv

from config import kw_load
from errors import NotFoundDocument
from word_mention import check_words_from_list

load_dotenv()

from connector import S3PDatabaseOutbox, S3PDatabaseFunction
from static import KeywordList, FoundKeywords

outbox = S3PDatabaseOutbox(5)
func = S3PDatabaseFunction(outbox)

kws = kw_load()

while True:
    try:
        for event in outbox.events():
            print(event)
            for kw in kws:
                fk = check_words_from_list(text=event.document.text, word_list=kw)
                print(fk)
                func.save(event, fk)
            outbox.success(event)
    except NotFoundDocument as error:
        print(error)
        time.sleep(5)


