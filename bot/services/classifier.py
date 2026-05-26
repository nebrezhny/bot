from __future__ import annotations

CLASSIFY_PROMPT = """
Determine the subject of this task in one word.
Reply with exactly one of: math / physics / chemistry / programming / russian / english / history / biology / other

Task: {text}

Reply (one word only):
"""


SUBJECT_MAP = [
    ('programming', ['функци', 'python', 'java', 'код', 'программа', 'скрипт', 'def ', 'class ', 'while', 'for ']),
    ('math', ['производн', 'интеграл', 'алгеб', 'геометр', 'числ', 'уравн', 'график']),
    ('chemistry', ['кипит', 'раствор', 'молекул', 'реакц', 'кислот', 'щелоч', 'вода']),
    ('physics', ['скорост', 'сила', 'энерг', 'давлен', 'масса', 'движен', 'тело']),
    ('english', ['translate', 'english', 'text', 'grammar', 'перевед', 'слов']),
    ('russian', ['орфограф', 'падеж', 'предлож', 'сочинен', 'стилист', 'букв', 'слова']),
    ('history', ['истор', 'войн', 'царь', 'побед', 'сражен', 'эпох']),
    ('biology', ['клетк', 'организм', 'растен', 'живот', 'биолог', 'фотоcинтез']),
]


def classify_text(task: str) -> str:
    normalized = task.lower()
    for subject, tokens in SUBJECT_MAP:
        if any(token in normalized for token in tokens):
            return subject
    return 'other'
