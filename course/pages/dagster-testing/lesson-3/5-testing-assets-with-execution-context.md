---
title: 'Урок 3: Тестирование ассетов с контекстом выполнения'
module: 'dagster_testing'
lesson: '3'
---

# Тестирование ассетов с контекстом выполнения

В Dagster ассеты могут принимать специальный необязательный аргумент `context`. Он предоставляет доступ к объекту `AssetExecutionContext`, открывающему соответствующие API ресурсов, конфигурации и логирования.

Если ассеты не используют API контекста, при тестировании не нужно заботиться о `context`.

Однако если переписать ассет `state_population_file`, добавив логирование через контекст, потребуется обновить тесты:

```python
# src/dagster_testing/defs/assets/lesson_3.py
@dg.asset()
def state_population_file_logging(context: dg.AssetExecutionContext) -> list[dict]:
    file_path = Path(__file__).absolute().parent / "../data/ny.csv"

    context.log.info(f"Reading file {file_path}")

    with open(file_path) as file:
        reader = csv.DictReader(file)
        return [row for row in reader]
```

Теперь тест этого ассета должен включать объект контекста. Следующий тест, работавший для ассета без `context`, завершится ошибкой:

```python
# tests/test_lesson_3.py
def test_state_population_file_logging_no_context(file_output):
    result = lesson_3.state_population_file_logging()
    assert result == file_output
```

Задать объект контекста для тестирования можно с помощью функции Dagster `build_asset_context`. Она позволяет установить параметр `context`:

```python
# tests/test_lesson_3.py
def test_state_population_file_logging(file_output):
    context = dg.build_asset_context()
    result = lesson_3.state_population_file_logging(context)
    assert result == file_output
```

Теперь тест должен пройти.

```bash
> pytest tests/test_lesson_3.py::test_state_population_file_logging
...
tests/test_lesson_3.py .                                                          [100%]
```

## Работа с контекстом при materialize()

Контекст можно обрабатывать и с помощью `materialize()`. Мы уже видели, что эта функция выполняет ассеты и предоставляет необходимые сведения о запуске:

```python
# tests/test_lesson_3.py
def test_assets_context(file_output):
    result = dg.materialize(
        assets=[lesson_3.state_population_file_logging],
    )
    assert result.success

    assert result.output_for_node("state_population_file_logging") == file_output
```

При использовании `dg.materialize()` не нужно явно передавать контекст.

### Передача контекста для партиционированных ассетов

Ещё одна ситуация, в которой может потребоваться контекст, — тестирование партиционированного ассета. Снова перепишем ассет `state_population_file`, теперь сделав его партиционированным. Определим три статические партиции, по одной для каждого файла штата в каталоге `data`:

```python
# src/dagster_testing/defs/assets/lesson_3.py
file_partitions = dg.StaticPartitionsDefinition(["ca.csv", "mn.csv", "ny.csv"])


@dg.asset(partitions_def=file_partitions)
def state_population_file_partition(context: dg.AssetExecutionContext) -> list[dict]:
    file_path = Path(__file__).absolute().parent / f"../data/{context.partition_key}"
    with open(file_path) as file:
        reader = csv.DictReader(file)
        return [row for row in reader]
```

Для выполнения этого ассета нужно передать одну из трёх партиций. Можно использовать `build_asset_context()` для создания объекта контекста и задания ключа партиции при тестировании:

```python
# tests/test_lesson_3.py
def test_state_population_file_partition(file_output):
    context = dg.build_asset_context(partition_key="ny.csv")
    assert lesson_3.state_population_file_partition(context) == file_output
```

```bash
> pytest tests/test_lesson_3.py::test_state_population_file_partition
...
tests/test_lesson_3.py .                                                          [100%]
```

По-прежнему можно выполнять ассеты с контекстом через `materialize()`, но потребуется указать конкретную партицию:

```python
# tests/test_lesson_3.py
def test_assets_partition(file_output):
    result = dg.materialize(
        assets=[
            lesson_3.state_population_file_partition,
        ],
        partition_key="ny.csv",
    )
    assert result.success

    assert result.output_for_node("state_population_file_partition") == file_output
```

```bash
> pytest tests/test_lesson_3.py::test_assets_partition
...
tests/test_lesson_3.py .                                                          [100%]
```

Важно помнить, что при материализации нескольких партиционированных ассетов через `materialize()`, как и при запуске в интерфейсе Dagster, нельзя выполнять их вместе, если они не имеют совместимого определения партиций для данного запуска. Например, если попытаться выполнить следующую материализацию с дополнительным ассетом, тест завершится ошибкой:

```python
# tests/test_lesson_3.py
def test_assets_multiple_partition() -> None:
    result = dg.materialize(
        assets=[
            lesson_3.state_population_file_partition,
            lesson_3.partition_asset_letter,
        ],
        partition_key="ny.csv",
    )
    assert result.success

    result.output_for_node("state_population_file_partition") == 1
    result.output_for_node("partition_asset_letter") == "A"
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
