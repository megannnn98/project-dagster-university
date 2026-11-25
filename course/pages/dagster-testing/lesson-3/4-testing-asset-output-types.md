---
title: 'Урок 3: Тестирование типов выходных данных ассетов'
module: 'dagster_testing'
lesson: '3'
---

# Тестирование типов выходных данных ассетов

В обычном Python функция может успешно выполняться, даже если её результат не соответствует аннотации типа. Например:

```python
# src/dagster_testing/defs/assets/lesson_3.py
def func_wrong_type() -> str:
    return 2
```

```python
# tests/test_lesson_3.py
def test_func_wrong_type():
    assert lesson_3.func_wrong_type() == 2
```

Приведённый тест пройдёт, хотя функция аннотирована как возвращающая `str`, а фактически возвращает `int`.

Одно из преимуществ Dagster — проверка типов при выполнении ассетов с аннотациями типов. Это помогает повысить качество данных и целостность пайплайнов, проверяя соответствие выходных данных ожидаемому типу.

Попробуем тот же пример с Dagster:

```python
# src/dagster_testing/defs/assets/lesson_3.py
@dg.asset
def wrong_type_annotation() -> str:
    return 2
```

```python
# tests/test_lesson_3.py
def test_wrong_type_annotation():
    assert lesson_3.wrong_type_annotation() == 2
```

Пройдёт ли тест? Нажми **View answer**, чтобы посмотреть ответ.

```bash {% obfuscated="true" %}
> pytest tests/test_lesson_3.py::test_wrong_type_annotation
...
tests/test_lesson_3.py F                        [100%]
...
E           dagster._core.errors.DagsterTypeCheckDidNotPass: Type check failed for op "wrong_type_annotation" output "result" - expected type "String". Description: Value "2" of python type "int" must be a string.
...
FAILED tests/test_lesson_3.py::test_wrong_type_annotation - dagster._core.errors.DagsterTypeCheckDidNotPass: Type check failed...
```

Поскольку Dagster проверяет типы в рамках собственного выполнения, обычно не нужно писать отдельные тесты, дублирующие эту проверку. Указывай аннотации типов для ассетов, где типы важны. Помни, что прямой вызов функции в обход материализации не обязательно выполняет проверку типов Dagster.

## Обработка исключений

Хотя отдельно проверять встроенный механизм контроля типов обычно не требуется, полезно писать тесты, проверяющие исключения. Например, можно убедиться, что ассет корректно завершается ошибкой, если не удаётся подключиться к базе данных или превышен лимит запросов API.

В `pytest` обработка исключений при тестировании Dagster происходит так же, как при тестировании обычных функций Python. Если бы мы хотели написать тест, проверяющий, что ассет `wrong_type_annotation` вызывает ошибку, он выглядел бы так:

```python
# src/dagster_testing/defs/assets/lesson_3.py
@dg.asset
def wrong_type_annotation() -> str:
    return 2
```

```python
# tests/test_lesson_3.py
def test_wrong_type_annotation_error():
    with pytest.raises(DagsterTypeCheckDidNotPass):
        lesson_3.wrong_type_annotation()
```

```bash
> pytest tests/test_lesson_3.py::test_wrong_type_annotation_error
...
tests/test_lesson_3.py .                                                          [100%]
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
