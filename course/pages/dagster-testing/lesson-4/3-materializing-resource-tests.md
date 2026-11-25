---
title: 'Урок 4: Тестирование материализации с ресурсами'
module: 'dagster_testing'
lesson: '4'
---

# Тестирование материализации с ресурсами

При обсуждении модульных тестов мы показали, как выполнять один или несколько ассетов вместе с помощью `dg.materialize()`. Мы по-прежнему можем материализовать ассеты таким способом, используя mock-объекты.

```python
# /tests/test_lesson_4.py
@patch("requests.get")
def test_state_population_api_assets(mock_get, example_response, api_output):
    mock_response = Mock()
    mock_response.json.return_value = example_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = dg.materialize(
        assets=[
            lesson_4.state_population_api_resource,
            lesson_4.total_population_resource,
        ],
        resources={"state_population_resource": lesson_4.StatePopulation()},
    )
    assert result.success

    assert result.output_for_node("state_population_api_resource") == api_output
    assert result.output_for_node("total_population_resource") == 9082539

```

```bash
> pytest tests/test_lesson_4.py::test_state_population_api_assets
...
tests/test_lesson_4.py .                                                          [100%]
```

Здесь используются те же подмена и mock-объект, что и раньше. Единственное отличие: поскольку ассету необходим ресурс, его нужно инициализировать и передать в `dg.materialize()`.

## Тестирование с materialize и конфигурацией

При материализации можно одновременно использовать ресурсы и конфигурации. Немного изменим ассет `state_population_api_resource_config`, чтобы он принимал конфигурацию запуска.

```python
# src/dagster_testing/defs/assets/lesson_4.py
class StateConfig(dg.Config):
    name: str


@dg.asset
def state_population_api_resource_config(
    config: StateConfig, state_population_resource: StatePopulation
) -> list:
    return state_population_resource.get_cities(config.name)
```

Теперь его можно выполнять с именем любого штата.

Чтобы написать тест с этим новым ассетом, необходимо указать и ресурсы, и `run_config` в `dg.materialize()`.

```python
# tests/test_lesson_4.py
@patch("requests.get")
def test_state_population_api_assets_config(mock_get, example_response, api_output):
    mock_response = Mock()
    mock_response.json.return_value = example_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = dg.materialize(
        assets=[
            lesson_4.state_population_api_resource_config,
            lesson_4.total_population_resource_config,
        ],
        resources={"state_population_resource": lesson_4.StatePopulation()},
        run_config=dg.RunConfig(
            {"state_population_api_resource_config": lesson_4.StateConfig(name="ny")}
        ),
    )
    assert result.success

    assert result.output_for_node("state_population_api_resource_config") == api_output
    assert result.output_for_node("total_population_resource_config") == 9082539
```

```bash
> pytest tests/test_lesson_4.py::test_state_population_api_assets_config
...
tests/test_lesson_4.py .                                                          [100%]
```

Функция `dg.materialize()` очень гибкая при тестировании и позволяет выполнить почти всё, что доступно при запуске ассетов в интерфейсе Dagster.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
