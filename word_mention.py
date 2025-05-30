import time

from flashtext import KeywordProcessor
from collections import defaultdict
from tqdm import tqdm
from pymystem3 import Mystem

from static import KeywordList, FoundKeywords


def check_words_from_list(text: str, word_list: KeywordList, lemmatize_words = True) -> FoundKeywords:
    """
        Анализирует текст на наличие слов/фраз из заданного списка с учетом лемматизации.

        Функция выполняет:

            1. Лемматизацию всего текста для приведения слов к начальной форме

            2. Поиск вхождений слов/фраз из списка:
           - Для отдельных слов проверяет совпадение лемм
           - Для словосочетаний ищет последовательности лемм

            3. Подсчет общего и уникального количества совпадений
    """

    stem = Mystem()

    # 1. Подготовка ключевых слов
    keyword_processor = KeywordProcessor(case_sensitive=False)
    keyword_dict = {}

    for item in word_list.elements:
        if lemmatize_words:
            # Лемматизация для отдельных слов
            if ' ' not in item:
                lemma = stem.lemmatize(item.lower())[0]
                keyword_dict[lemma] = item
            # Для фраз лемматизируем каждое слово
            else:
                phrase_lemmas = [stem.lemmatize(w.lower())[0] for w in item.split()]
                keyword_dict[' '.join(phrase_lemmas)] = item
        else:
            keyword_dict[item.lower()] = item

    for lemmatized_word, original_word in keyword_dict.items():
        keyword_processor.add_keyword(lemmatized_word, original_word)

    # 2. Лемматизация текста
    start_time = time.time()
    text_lemmas = stem.lemmatize(text.lower())
    clean_text = ' '.join([lem.strip() for lem in text_lemmas if lem.strip()])
    print(f"Лемматизация выполнена за {time.time() - start_time:.2f} сек.")

    # 3. Поиск ключевых слов
    start_time = time.time()
    found_keywords = keyword_processor.extract_keywords(clean_text)

    # 4. Подсчет результатов
    word_counts = defaultdict(int)
    for kw in found_keywords:
        word_counts[kw] += 1

    print(f"Поиск выполнен за {time.time() - start_time:.2f} сек.")
    return FoundKeywords(word_list, dict(word_counts))
