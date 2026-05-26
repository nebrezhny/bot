from bot.services.classifier import classify_text


def test_classifier_math():
    assert classify_text('найдите производную x^2') == 'math'


def test_classifier_programming():
    assert classify_text('напишите функцию на python') == 'programming'


def test_classifier_chemistry_or_physics():
    assert classify_text('при какой температуре кипит вода') in {'chemistry', 'physics'}
