#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Консольное приложение для анализа текстовых файлов.
Выполняет:
- чтение файла
- подсчёт общего количества слов
- поиск заданного слова и подсчёт его повторений
- обработку ошибок ввода/вывода
- базовое тестирование функции поиска
"""

import sys
import re
from pathlib import Path
from typing import Tuple


def read_file(file_path: str) -> str:
    """
    Считывает содержимое текстового файла.
    В Python строка передаётся по ссылке (но неизменяема),
    что условно соответствует 'владению' и 'неизменяемому заимствованию'.

    Args:
        file_path: путь к файлу

    Returns:
        Содержимое файла в виде строки

    Raises:
        FileNotFoundError: если файл не найден
        IOError: при других ошибках ввода/вывода
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    try:
        # Используем кодировку UTF-8, как наиболее распространённую
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Пробуем другие распространённые кодировки
        try:
            return path.read_text(encoding='cp1251')
        except Exception as e:
            raise IOError(f"Не удалось декодировать файл: {e}")
    except Exception as e:
        raise IOError(f"Ошибка чтения файла: {e}")


def count_words(text: str) -> int:
    """
    Подсчитывает количество слов в тексте.
    Словом считается последовательность букв, цифр и апострофов,
    ограниченная символами-разделителями (пробелы, пунктуация и т.д.).

    Args:
        text: исходный текст (передаётся по ссылке, неизменяемый)

    Returns:
        Количество слов
    """
    # Регулярное выражение: \w+ (буквы, цифры, подчёркивание) + разрешим апостроф
    words = re.findall(r"[A-Za-zА-Яа-я0-9']+", text)
    return len(words)


def count_word_occurrences(text: str, word: str) -> int:
    """
    Подсчитывает количество вхождений заданного слова в текст.
    Поиск ведётся по полному совпадению слова (с учётом границ).
    Регистр учитывается (можно легко изменить, приведя к lower()).

    Args:
        text: исходный текст (неизменяемая ссылка)
        word: искомое слово (неизменяемая ссылка)

    Returns:
        Количество повторений
    """
    # Экранируем специальные символы в слове и строим границы слова \b
    pattern = r'\b' + re.escape(word) + r'\b'
    matches = re.findall(pattern, text, flags=re.UNICODE)
    return len(matches)


def analyze_file(file_path: str, search_word: str) -> Tuple[int, int]:
    """
    Выполняет полный анализ файла: чтение, подсчёт слов и вхождений.

    Args:
        file_path: путь к файлу
        search_word: слово для поиска

    Returns:
        Кортеж (общее количество слов, количество вхождений search_word)
    """
    content = read_file(file_path)  # передача строки (владение)
    total_words = count_words(content)  # неизменяемое заимствование content
    occurrences = count_word_occurrences(content, search_word)
    return total_words, occurrences


def run_tests() -> None:
    """Базовый тест для проверки функции поиска слова."""
    print("Запуск тестов...")

    # Тест 1: обычный текст
    text1 = "Hello world! Hello again. Hello, hello?"
    word1 = "Hello"
    expected1 = 3  # регистрозависимо: 'Hello' три раза (world, again, hello? - не подходит из-за регистра)
    result1 = count_word_occurrences(text1, word1)
    assert result1 == expected1, f"Тест 1 провален: ожидалось {expected1}, получено {result1}"

    # Тест 2: слово с границами (не должно находиться внутри другого слова)
    text2 = "cat catalog cat cat's cat"
    word2 = "cat"
    expected2 = 3  # catalog и cat's не считаются
    result2 = count_word_occurrences(text2, word2)
    assert result2 == expected2, f"Тест 2 провален: ожидалось {expected2}, получено {result2}"

    # Тест 3: пустой текст
    assert count_word_occurrences("", "any") == 0, "Тест 3 провален (пустой текст)"

    # Тест 4: слово отсутствует
    assert count_word_occurrences("one two three", "four") == 0, "Тест 4 провален (отсутствует)"

    # Тест 5: регистр (проверка, что по умолчанию регистр важен)
    text5 = "Word word WORD"
    assert count_word_occurrences(text5, "Word") == 1, "Тест 5A провален"
    assert count_word_occurrences(text5, "word") == 1, "Тест 5B провален"
    assert count_word_occurrences(text5, "WORD") == 1, "Тест 5C провален"

    # Дополнительно тестируем count_words
    assert count_words("one two three") == 3
    assert count_words("Hello, world!") == 2
    assert count_words("") == 0

    print("✅ Все тесты пройдены успешно!")


def print_usage() -> None:
    """Выводит справку по использованию программы."""
    print("""
Использование:
    python word_counter.py <путь_к_файлу> <слово_для_поиска>
    python word_counter.py --test

Пример:
    python word_counter.py document.txt пример
    python word_counter.py --test   (запуск тестов)
""")


def main() -> None:
    """Главная функция приложения. Обрабатывает аргументы командной строки."""
    args = sys.argv[1:]

    # Режим тестирования
    if len(args) == 1 and args[0] == "--test":
        run_tests()
        return

    # Режим анализа файла
    if len(args) != 2:
        print("Ошибка: неверное количество аргументов.")
        print_usage()
        sys.exit(1)

    file_path, search_word = args[0], args[1]

    try:
        total_words, occurrences = analyze_file(file_path, search_word)
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        sys.exit(2)
    except IOError as e:
        print(f"Ошибка ввода/вывода: {e}")
        sys.exit(3)
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        sys.exit(4)

    # Вывод результатов в требуемом формате
    print(f"Общее количество слов в файле: {total_words}")
    print(f"Количество повторений слова '{search_word}': {occurrences}")


if __name__ == "__main__":
    main()