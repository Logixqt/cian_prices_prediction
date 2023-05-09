import random
import re
import string
from typing import List, Union

import pymorphy2

_MORPH = pymorphy2.MorphAnalyzer()

# набор регулярных выражений для обработки текста
_PREPROCESSING_EXPRESSIONS = [
    ("(@|#)[A-Za-z0-9А-Яа-яЁё_]+", " "),
    ("\[(id|club)\d{5,20}\|[A-Za-z0-9А-Яа-яЁё_/ ]*\]", " "),
    ("https://[A-Za-z0-9.]*/[A-Za-z0-9.\-_/?+]*", " "),
    ("&quot;", " "),
    ("₽", "руб "),
    ("&quot", " "),
    ("(<br>|;|&|:)", ". "),
    ("[^A-Za-z0-9А-Яа-яЁё_\-+*.,_×/%?!;()«»']+", " "),
    *[("(__|; ;|~~|~ ~|;;)+", " "), ("(\. \.|\.\.| \.)+", ". "), ("^\.", " ")],
]

def clean_text(text: str) -> str:
    """
    Осуществляет обработку строки используя:
     - набор регулярных выражений `_PREPROCESSING_EXPRESSIONS`;
     - изменение регистра.

    Args:
        text:  str, строка, которую необходимо обработать

    Returns:
        str, обработанная строка.
    """
    if not isinstance(text, str):
        return ""
    
    text = text.lower()

    for reg_exp in _PREPROCESSING_EXPRESSIONS:
        expression = reg_exp[0]
        replace_str = reg_exp[1]
        text = " ".join(re.sub(expression, replace_str, text).split())

    text = [token for token in text.split(" ")]
    text_new = []
    for token_idx in range(len(text)):
        if len(text[token_idx]) == 0:
            continue
        token = text[token_idx]
        for punct in string.punctuation:
            token = token.replace(punct, ' ')
        text_new.append(token)

    text_new = " ".join(text_new)
    return text_new

def strip_special_characters(text: str) -> str:
    """
    Удалят символы (не буквы и не цифры) из начала и конца входящей строки.

    Args:
        text: str, строка, из которой необходимо удалить символы

    Returns:
        str, обработанная строка.
    """

    pattern = re.compile("\A\W+|\W+\Z")
    result = pattern.sub("", text)
    return result


def remove_stopwords(text: str, stopwords: List[str]) -> str:
    """
    Удалят из входящей строки указанные стоп-слова.

    Args:
        text: str, строка, из которой необходимо удалить слова
        stopwords: List[str], список из слов, которые необходимо удалить из входящей
            строки `text`

    Returns:
        str, строка, не содержащая стоп-слов.
    """
    return " ".join(
        [
            word
            for word in text.split()
            if not any([stp_word in word for stp_word in stopwords])
        ]
    )

def rstrip_auxiliary_pos(tokens: List[str]) -> List[str]:
    """
    Удаляет служебные части речи (местоимения, предлоги, союзы, частицы и междометия) из
    конца листа токенов.

    tokens: List[str], список токенов, из которого необходимо удалить служебные части
        речи

    Returns:
        List[str], обновленный список токенов, не содержащий служебные части речи.
    """
    if not tokens:
        return tokens

    parsed_last_token = _MORPH.parse(tokens[-1])[0]
    if any(
        [
            pos in parsed_last_token.tag
            for pos in ["NPRO", "PREP", "CONJ", "PRCL", "INTJ"]
        ]
    ):
        return rstrip_auxiliary_pos(tokens[:-1])
    else:
        return tokens
    
    
def strip_auxiliary_pos(tokens: List[str]) -> List[str]:
    """
    Удаляет служебные части речи (местоимения, предлоги, союзы, частицы и междометия) из
    листа токенов.

    tokens: List[str], список токенов, из которого необходимо удалить служебные части
        речи

    Returns:
        List[str], обновленный список токенов, не содержащий служебные части речи.
    """
    if not tokens:
        return tokens
    
    tokens_to_drop = []
    for token in tokens:
        parsed_token = _MORPH.parse(tokens[-1])[0]
        if any(
            [
                pos in parsed_token.tag
                for pos in ["NPRO", "PREP", "CONJ", "PRCL", "INTJ"]
            ]
        ):
            tokens_to_drop.append(token)
    return [token for token in tokens if token not in tokens_to_drop]

def remove_punctuation(text: str) -> str:
    return text.translate(
        str.maketrans(string.punctuation, " " * len(string.punctuation))
    )

# def normalize_text(text: str) -> str:
#     tokens = text.split()
#     norm_text = " ".join([_MORPH.parse(tok)[0].normal_form for tok in tokens])
#     return norm_text

def normalize_text(text: str) -> str:
    tokens = text.split()
    tokens_norm = [_MORPH.parse(tok)[0].normal_form for tok in tokens]
    norm_text = " ".join(strip_auxiliary_pos(tokens_norm))
    return norm_text