---
title: 'Урок 3: Тестирование зависимостей'
module: 'dagster_testing'
lesson: '3'
---

# Тестирование зависимостей

Большинство графов ассетов Dagster содержит несколько ассетов, зависящих от результатов других ассетов. Именно связывание ассетов определяет структуру графа. Когда ассеты получают входные данные, которые сами не контролируют, важно по-прежнему создавать детерминированные тесты с предсказуемым результатом.

Добавим нижестоящий ассет для `state_population_file`, принимающий его результат:

```python
# src/dagster_testing/defs/assets/lesson_3.py
@dg.asset
def total_population(state_population_file: list[dict]) -> int:
    return sum([int(x["Population"]) for x in state_population_file])
```

Приведённый код определяет ассет `total_population`, который:

1. Принимает список словарей, возвращённый ассетом `state_population_file`.
2. Возвращает суммарное население всех городов списка.

Связь между `state_population_file` и `total_population` определяется входным параметром `total_population`. Как будет выглядеть тест этого ассета? Нажми **View answer**, чтобы посмотреть ответ.

```python {% obfuscated="true" %}
# tests/test_lesson_3.py
def test_total_population():
    state_populations = [
        {
            "City": "New York",
            "Population": "8804190",
        },
        {
            "City": "Buffalo",
            "Population": "278349",
        },
        {
            "City": "Yonkers",
            "Population": "211569",
        },
    ]

    assert lesson_3.total_population(state_populations) == 9294108
```

Поскольку мы сами задаём входной параметр `total_population`, можно заранее определить ожидаемый результат. В данном случае суммарное население трёх городов составляет 9 294 108 человек.

Как и предыдущий тест ассета, этот тест выглядит как обычный код Python. Его также можно запустить с помощью `pytest`:

```bash
> pytest tests/test_lesson_3.py::test_total_population
...
tests/test_lesson_3.py .                                                          [100%]
```

## Тестирование материализаций

По мере усложнения пайплайнов полезно тестировать материализацию ассетов Dagster. Функция `dg.materialize()` выполняет ассеты и возвращает объект `dagster.ExecuteInProcessResult`. Затем можно проверить свойство `success`, чтобы убедиться, что всё материализовалось ожидаемым образом.

Поскольку ассет `total_population` зависит только от результата `state_population_file`, мы можем материализовать оба ассета вместе и убедиться в их корректной работе:

```python
# tests/test_lesson_3.py
def test_assets():
    _assets = [
        lesson_3.state_population_file,
        lesson_3.total_population,
    ]
    result = dg.materialize(_assets)
    assert result.success
```

```bash
> pytest tests/test_lesson_3.py::test_assets
...
tests/test_lesson_3.py .                                                          [100%]
```

Успешная материализация — хорошее начало, но нужно также проверить возвращаемые значения каждого ассета. К счастью, результат `materialize()` позволяет получить выходное значение каждого ассета с помощью метода `output_for_node()`:

```python
# tests/test_lesson_3.py
def test_assets():
    _assets = [
        lesson_3.state_population_file,
        lesson_3.total_population,
    ]
    result = dg.materialize(_assets)
    assert result.success

    state_populations = [
        {
            "City": "New York",
            "Population": "8804190",
        },
        {
            "City": "Buffalo",
            "Population": "278349",
        },
        {
            "City": "Yonkers",
            "Population": "211569",
        },
    ]
    assert result.output_for_node("state_population_file") == state_populations
    assert result.output_for_node("total_population") == 9294108
```

С помощью `output_for_node()` получаем результаты отдельных ассетов и проверяем, что они соответствуют ожиданиям.

## Логирование

Поскольку ассеты выполняются средствами Dagster, при вызове `materialize()` в журнал записываются стандартные события выполнения Dagster. Если повторно запустить `pytest` с флагом `-s`, отключающим перехват вывода, вместе с результатами тестов будут показаны логи Dagster:

```bash
> pytest tests/test_lesson_3.py::test_assets -s
...
tests/test_lesson_3.py 2025-02-14 09:30:11 -0600 - dagster - DEBUG - __ephemeral_asset_job__ - 7924f6b8-72c6-4789-b34a-d25b144f7f66 - 62349 - RUN_START - Started execution of run for "__ephemeral_asset_job__".
2025-02-14 09:30:11 -0600 - dagster - DEBUG - __ephemeral_asset_job__ - 7924f6b8-72c6-4789-b34a-d25b144f7f66 - 62349 - ENGINE_EVENT - Executing steps in process (pid: 62349)
2025-02-14 09:30:11 -0600 - dagster - DEBUG - __ephemeral_asset_job__ - 7924f6b8-72c6-4789-b34a-d25b144f7f66 - 62349 - RESOURCE_INIT_STARTED - Starting initialization of resources [io_manager].
...
```

Логи полезны при отладке упавшего теста и помогают локализовать ошибку.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
