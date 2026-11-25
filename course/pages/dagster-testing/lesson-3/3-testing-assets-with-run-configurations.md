---
title: 'Урок 3: Тестирование ассетов с конфигурациями запуска'
module: 'dagster_testing'
lesson: '3'
---

# Тестирование ассетов с конфигурациями запуска

Некоторые ассеты в пайплайнах Dagster могут принимать параметры, определённые вне выходных данных других ассетов. Обычно это конфигурации запуска, задаваемые во время выполнения.

Сейчас ассет `state_population_file` может разобрать только один файл. Создадим новый ассет `state_population_file_config` с конфигурацией запуска. Он сможет обрабатывать произвольный файл:

```python
# src/dagster_testing/defs/assets/lesson_3.py
class FilepathConfig(dg.Config):
    path: str


@dg.asset
def state_population_file_config(config: FilepathConfig) -> list[dict]:
    with open(config.path) as file:
        reader = csv.DictReader(file)
        return [row for row in reader]
```

Теперь напишем новый тест этого ассета. Поскольку можно передать любой файл, воспользуемся файлом `test.csv` из каталога `tests/data`. Этот файл имеет ту же схему, что и `ny.csv`, но содержит тестовые данные.

```
City,Population
Example 1,4500000
Example 2,3000000
Example 3,1000000
```

Для тестирования ассета с конфигурацией запуска нужно передать требуемую конфигурацию в качестве входного параметра. Вот как будет выглядеть тест. Нажми **View answer**, чтобы посмотреть ответ.

```python {% obfuscated="true" %}
# tests/test_lesson_3.py
def test_state_population_file_config():
    file_path = Path(__file__).absolute().parent / "data/test.csv"

    config_file = assets.FilepathConfig(path=file_path.as_posix())
    assert lesson_3.state_population_file_config(config_file) == [
        {
            "City": "Example 1",
            "Population": "4500000",
        },
        {
            "City": "Example 2",
            "Population": "3000000",
        },
        {
            "City": "Example 3",
            "Population": "1000000",
        },
    ]
```

```bash
> pytest tests/test_lesson_3.py::test_state_population_file_config
...
tests/test_lesson_3.py .                                                          [100%]
```

## Фикстуры pytest

При совместном использовании Dagster и `pytest` можно воспользоваться возможностями `pytest`, чтобы упростить повторное использование тестового кода. Если `FilepathConfig` используется несколькими тестами, полезно создать фикстуру `pytest`:

```python
# tests/test_lesson_3.py
@pytest.fixture()
def config_file():
    file_path = Path(__file__).absolute().parent / "data/test.csv"
    return lesson_3.FilepathConfig(path=file_path.as_posix())


def test_state_population_file_config_fixture_1(config_file):
    assert lesson_3.state_population_file_config(config_file) == [
        {
            "City": "Example 1",
            "Population": "4500000",
        },
        {
            "City": "Example 2",
            "Population": "3000000",
        },
        {
            "City": "Example 3",
            "Population": "1000000",
        },
    ]
```

```bash
> pytest tests/test_lesson_3.py::test_state_population_file_config_fixture_1
tests/test_lesson_3.py .                                                          [100%]
```

## Несколько фикстур pytest

Фикстуры упрощают чтение тестового кода и позволяют объединить части, используемые несколькими тестами. Тесты могут использовать несколько фикстур. Например, можно добавить дополнительную фикстуру для ожидаемого результата функции:

```python
# tests/test_lesson_3.py
@pytest.fixture()
def config_file():
    file_path = Path(__file__).absolute().parent / "data/test.csv"
    return lesson_3.FilepathConfig(path=file_path.as_posix())


@pytest.fixture()
def file_example_output():
    return [
        {
            "City": "Example 1",
            "Population": "4500000",
        },
        {
            "City": "Example 2",
            "Population": "3000000",
        },
        {
            "City": "Example 3",
            "Population": "1000000",
        },
    ]


def test_state_population_file_config_fixture_2(config_file, file_example_output):
    assert lesson_3.state_population_file_config(config_file) == file_example_output
```

```bash
> pytest tests/test_lesson_3.py::test_state_population_file_config_fixture_2
...
tests/test_lesson_3.py .                                                          [100%]
```

## Передача конфигурации запуска при материализации

Для передачи конфигурации запуска при материализации необходимо указать дополнительный параметр `run_config` в вызове `materialize()`. Этот параметр принимает объект `RunConfig`, сопоставляющий конкретную конфигурацию запуска с ассетом, которому она необходима:

```python
# tests/test_lesson_3.py
def test_assets_config(config_file, file_example_output):
    _assets = [
        lesson_3.state_population_file_config,
        lesson_3.total_population_config,
    ]
    result = dg.materialize(
        assets=_assets,
        run_config=dg.RunConfig({"state_population_file_config": config_file}),
    )
    assert result.success

    assert result.output_for_node("state_population_file_config") == file_example_output
    assert result.output_for_node("total_population_config") == 8500000
```

```bash
> pytest tests/test_lesson_3.py::test_assets_config
...
tests/test_lesson_3.py .                                                          [100%]
```

Конфигурацию также можно передать с помощью YAML в формате, аналогичном интерфейсу Dagster. Вот та же конфигурация запуска в YAML:

```yaml
ops:
  state_population_file_config:
    config:
      path: "tests/data/test.csv"
```

Затем обновим параметр `run_config`, чтобы использовать этот YAML-файл:

```python {% obfuscated="true" %}
# tests/test_lesson_3.py
def test_assets_config_yaml(file_example_output):
    _assets = [
        lesson_3.state_population_file_config,
        lesson_3.total_population_config,
    ]
    result = dg.materialize(
        assets=_assets,
        run_config=yaml.safe_load(
            (Path(__file__).absolute().parent / "configs/lesson_3.yaml").open()
        ),
    )
    assert result.success

    assert result.output_for_node("state_population_file_config") == file_example_output
    assert result.output_for_node("total_population_config") == 8500000
```

```bash
> pytest tests/test_lesson_3.py::test_assets_config_yaml
...
tests/test_lesson_3.py .                                                          [100%]
```

При выполнении тестов результат использования `dg.RunConfig` или эквивалентной конфигурации из YAML одинаков. YAML может оказаться удобнее для чтения сложных конфигураций или хранения примеров для пользователей, которые будут запускать выполнение через интерфейс Dagster.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
