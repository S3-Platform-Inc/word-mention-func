import time
from tqdm import tqdm


def check_words_from_list(stem, text, word_list, lemmatize_words_from_list = True):
    """
        Анализирует текст на наличие слов/фраз из заданного списка с учетом лемматизации.

        Функция выполняет:

            1. Лемматизацию всего текста для приведения слов к начальной форме

            2. Поиск вхождений слов/фраз из списка:
           - Для отдельных слов проверяет совпадение лемм
           - Для словосочетаний ищет последовательности лемм

            3. Подсчет общего и уникального количества совпадений

        Args:
            stem (Mystem): Экземпляр Mystem для лемматизации
            text (str): Анализируемый текст
            word_list (list): Список слов/фраз для поиска
            lemmatize_words_from_list (bool) = True: Необходимость лемматизации отдельных слов из списка

        Returns:
            tuple:
                - list: Все совпавшие элементы из word_list
                - int: Общее количество совпадений
                - int: Количество уникальных совпадений
    """

    print('Лемматизация текста...')
    start_time = time.time()
    text_lemmas = stem.lemmatize(text.lower())  # Лемматизация всего текста (список из нач. форм)
    end_time = time.time()
    print(f"Лемматизация текста выполнена! ({(end_time - start_time)} с.)")


    mentioned_words = []
    # Цикл по элементам списка слов
    for item in tqdm(word_list, desc=f'Обработка слов из списка'):
        if ' ' in item:  # Обработка словосочетаний (если есть пробел в элементе списка)
            phrase_lemmas = stem.lemmatize(item.lower())  # список из нач. форм слов в словосочетании
            phrase_lemmas = [p for p in phrase_lemmas if p.isalnum()] # исключение из списка пробелов и переносов
            len_p = len(phrase_lemmas) # длина словосочетания
            # Поиск всех вхождений фразы
            # Цикл по длине всего текста
            for i in range(len(text_lemmas) - len_p + 1):
                # Если фрагмент текста с i-го места до i+len_p (длина словосочетания) совпадает со словосочетанием из списка
                if text_lemmas[i:i + len_p] == phrase_lemmas:
                    mentioned_words.append(item)
        else:  # Обработка отдельных слов
            # Лемматизация элемента списка слов
            if lemmatize_words_from_list:
                lemma = stem.lemmatize(item.lower())[0]
            else:
                lemma = item
            # Подсчет вхождений этого слова в текст
            for text_lemma in text_lemmas:
                if text_lemma == lemma:
                    mentioned_words.append(item)

    return mentioned_words, len(mentioned_words), len(set(mentioned_words))
