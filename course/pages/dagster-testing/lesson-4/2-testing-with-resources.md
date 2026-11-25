---
title: 'Урок 4: Тестирование с ресурсами'
module: 'dagster_testing'
lesson: '4'
---

# Тестирование с ресурсами

В Dagster внешние зависимости не всегда определяются непосредственно внутри ассетов. Обычно они переиспользуются несколькими ассетами. Здесь пригодятся ресурсы.

Ресурсы — объекты, предоставляющие доступ к внешним системам, базам данных или сервисам и используемые для управления зависимостями в Dagster.

Можно вынести код работы с API из ассета в ресурс. В данном примере ресурс представляет собой класс, наследуемый от `dg.ConfigurableResource`. Он может иметь любое количество методов, используемых ассетами. В нашем ресурсе будет только один метод — `get_cities`.

```python
# src/dagster_testing/defs/assets/lesson_4.py
class StatePopulation(dg.ConfigurableResource):
    def get_cities(self, state: str) -> list[dict]:
        output = []
        try:
            response = requests.get(API_URL, params={"state": state})
            response.raise_for_status()

            for doc in response.json().get("cities"):
                output.append(
                    {
                        "city": doc.get("city_name"),
                        "population": doc.get("city_population"),
                    }
                )

            return output

        except requests.exceptions.RequestException:
            return output
```

Этот код практически не изменился по сравнению с ассетом `state_population_api`. Он подключается к API, получает JSON и возвращает разобранные результаты.

Поскольку теперь ресурс содержит всю логику подключения к API, можно написать новый ассет, вызывающий его метод:

```python
# src/dagster_testing/defs/assets/lesson_4.py
@dg.asset
def state_population_api_resource(
    state_population_resource: StatePopulation,
) -> list[dict]:
    return state_population_resource.get_cities("ny")
```

## Тестирование ресурсов

Наш ассет изменился. Теперь для его выполнения требуется инициализированный ресурс `StatePopulation`:

```python
assets.state_population_api_resource(assets.StatePopulation())
```

Но основная логика осталась неизменной. Что нужно изменить в тесте? Нажми **View answer**, чтобы посмотреть ответ.

```python {% obfuscated="true" %}
# tests/test_lesson_4.py
@patch("requests.get")
def test_state_population_api_resource_mock(mock_get, example_response):
    mock_response = Mock()
    mock_response.json.return_value = example_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = lesson_4.state_population_api_resource(lesson_4.StatePopulation())

    assert len(result) == 2
    assert result[0] == {
        "city": "New York",
        "population": 8804190,
    }
    mock_get.assert_called_once_with(lesson_4.API_URL, params={"state": "ny"})

```

```bash
> pytest tests/test_lesson_4.py::test_state_population_api_resource_mock
...
tests/test_lesson_4.py .                                                          [100%]
```

На удивление немногое. По-прежнему нужно подменить метод `requests.get`, поэтому вся настройка mock-объектов останется прежней. Главное отличие в том, что запрос выполняется ресурсом, а не самим ассетом. С точки зрения тестирования это почти ничего не меняет, поэтому практически весь тест сохраняется.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
