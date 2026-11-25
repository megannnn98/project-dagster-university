---
title: 'Урок 4: Подмена ресурсов при тестировании'
module: 'dagster_testing'
lesson: '4'
---

# Подмена ресурсов при тестировании

При совместном использовании mock-объектов и ресурсов иногда проще подменить сам ресурс, а не лежащую в его основе функцию. Можно вообще не подменять `requests.get`, а вместо этого имитировать ресурс `StatePopulation`.

Вспомним два вопроса, которые нужно учитывать при подмене сервиса:

1. Какой сервис нужно имитировать.
2. Как имитируемый сервис должен работать, чтобы удовлетворить требованиям теста.

Теперь нужно имитировать `StatePopulation`. Что касается необходимой функциональности, нам требуется подменить ответ метода `get_cities`. Значит, можно не заботиться о `requests`.

Сначала создадим ещё одну `pytest.fixture` с примером ответа `get_cities`.

```python
# tests/test_lesson_4.py
@pytest.fixture
def fake_city():
    return {
        "city": "Fakestown",
        "population": 42,
    }
```

Затем настроим mock-объект, задав возвращаемое значение.

```python
mocked_resource = Mock()
mocked_resource.get_cities.return_value = [fake_city]
```

Это всё, что нужно для написания нового теста ассета `state_population_api_resource`. Помни, что декоратор patch больше не требуется, поскольку `requests` не нужен. Как будет выглядеть тест? Нажми **View answer**, чтобы посмотреть ответ.

```python {% obfuscated="true" %}
# tests/test_lesson_4.py
def test_state_population_api_mocked_resource(fake_city):
    mocked_resource = Mock()
    mocked_resource.get_cities.return_value = [fake_city]

    result = lesson_4.state_population_api_resource(mocked_resource)

    assert len(result) == 1
    assert result[0] == fake_city
```

# Материализация с подменёнными ресурсами

Подменённый ресурс можно также использовать в `dg.materialize()`, если нужно выполнить несколько ассетов в одном тесте:

```python
# tests/test_lesson_4.py
def test_state_population_api_assets_mocked_resource(fake_city):
    mocked_resource = Mock()
    mocked_resource.get_cities.return_value = [fake_city]

    result = dg.materialize(
        assets=[
            lesson_4.state_population_api_resource_config,
            lesson_4.total_population_resource_config,
        ],
        resources={"state_population_resource": mocked_resource},
        run_config=dg.RunConfig(
            {"state_population_api_resource_config": lesson_4.StateConfig(name="ny")}
        ),
    )
    assert result.success

    assert result.output_for_node("state_population_api_resource_config") == [fake_city]
    assert result.output_for_node("total_population_resource_config") == 42
```

```bash
> pytest tests/test_lesson_4.py::test_state_population_api_assets_mocked_resource
...
tests/test_lesson_4.py .                                                          [100%]
```

## Когда подменять ресурс

Возможно, ты задаёшься вопросом, когда следует подменять ресурс, а когда — используемые им функции. Как правило, функции внутри ресурса следует подменять, если тебя интересует тестирование реализации самого ресурса. Методы ресурса можно подменять, когда основная цель — тестирование функциональности ассетов.

Подмена самого ресурса также даёт больше контроля над ожидаемыми результатами конкретных функций. Это облегчает написание тестов для ассетов, использующих несколько ресурсов или ресурсы с состоянием.

Используй эту таблицу как краткую памятку:

| Подменяй функции, когда | Подменяй ресурсы, когда |
| ------------------- | ------------------- |
| Тестируешь реализацию ресурса | Тестируешь логику ассета |
| Нужно проверить параметры вызова | Тестируешь граф ассетов |
| Ресурс имеет простой интерфейс | Ресурс имеет несколько методов |
| Тестируешь обработку ошибок | Тестируешь успешный сценарий |

На практике подмена ресурсов часто оказывается более чистым подходом для тестирования ассетов, поскольку тест сосредоточен на том, что делает ассет, а не на внутренней реализации ресурса.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
