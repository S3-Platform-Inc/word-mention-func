import time
from tqdm import tqdm


def check_words_from_list(stem, text, word_list):
    """
    Проверяет, содержит ли текст словосочетания/слова из списков в любой форме,
    возвращает общее количество вхождений по каждому списку и результат проверки порога.

    Args:
        text (str): Проверяемый текст.
        word_list: Списки с словами/фразами в начальной форме.

    Returns:
        tuple: ttt
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
            lemma = stem.lemmatize(item.lower())[0]
            # Подсчет вхождений этого слова в текст
            for text_lemma in text_lemmas:
                if text_lemma == lemma:
                    mentioned_words.append(item)

    return mentioned_words, len(mentioned_words), len(set(mentioned_words))
