import time
from tqdm import tqdm


def check_words_in_lists(stem, text, threshold, word_lists):
    """
    Проверяет, содержит ли текст словосочетания/слова из списков в любой форме,
    возвращает общее количество вхождений по каждому списку и результат проверки порога.

    Args:
        text (str): Проверяемый текст.
        threshold (int): Минимальное общее количество вхождений.
        word_lists: Списки с словами/фразами в начальной форме.

    Returns:
        tuple: (список счетчиков вхождений для каждого списка, 1/0 - превышен ли порог)
    """

    print('Лемматизация текста...')
    start_time = time.time()  # Фиксируем начальное время [[3]][[5]]
    text_lemmas = stem.lemmatize(text.lower())  # Лемматизация всего текста (список из нач. форм)
    end_time = time.time()
    print(f"Лемматизация текста выполнена! ({end_time - start_time} с.)")
    counts = []  # Подсчет совпавших слов из каждого списка
    total = 0  # Общее число совпавших слов

    # Цикл по спискам слов
    for num, word_list in enumerate(word_lists):
        list_count = 0  # Кол-во совпавших слов
        # Цикл по элементам списка слов
        for item in tqdm(word_list, desc=f'Обработка слов из списка №{num+1}'):
            if ' ' in item:  # Обработка словосочетаний (если есть пробел в элементе списка)
                phrase_lemmas = stem.lemmatize(item.lower())  # список из нач. форм слов в словосочетании
                phrase_lemmas = [p for p in phrase_lemmas if p.isalnum()] # исключение из списка пробелов и переносов
                len_p = len(phrase_lemmas) # длина словосочетания
                # Поиск всех вхождений фразы
                # Цикл по длине всего текста
                for i in range(len(text_lemmas) - len_p + 1):
                    # Если фрагмент текста с i-го места до i+len_p (длина словосочетания) совпадает со словосочетанием из списка
                    if text_lemmas[i:i + len_p] == phrase_lemmas:
                        list_count += 1
            else:  # Обработка отдельных слов
                # Лемматизация элемента списка слов
                lemma = stem.lemmatize(item.lower())[0]
                # Подсчет вхождений этого слова в текст
                list_count += text_lemmas.count(lemma)
        counts.append(list_count)
        total += list_count

    return counts, 1 if total >= threshold else 0
