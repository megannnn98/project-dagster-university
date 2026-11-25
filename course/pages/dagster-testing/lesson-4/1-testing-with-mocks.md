---
title: 'Урок 4: Тестирование с mock-объектами'
module: 'dagster_testing'
lesson: '4'
---

# Тестирование с mock-объектами

До сих пор ни один из созданных ассетов не подключался к другим сервисам. При построении настоящей платформы данных это редко бывает так. Даже платформа небольшой организации использует десятки внешних систем.

В уроке 2 наш пайплайн загружал данные о населении городов из локального CSV. Как бы он выглядел, если бы вместо этого мы запрашивали данные о городах через API?

Представим, что существует API для получения численности населения городов по штатам (к сожалению, в действительности такого API нет, но для тестирования это неважно). Допустим, конечная точка API находится на `fake.com`, а пример запроса для конкретного штата выглядит так:

```bash
> curl -X GET "https://fake.com/population.json?state=ny" -H "Accept: application/json"

{
  "cities": [
    {"name": "New York City", "population": 8804190},
    {"name": "Buffalo", "population": 278349},
    {"name": "Rochester", "population": 211328},
    {"name": "Yonkers", "population": 201344},
    {"name": "Syracuse", "population": 148620}
    ...
  ]
}
```

Перепишем ассет `state_population_file`, чтобы вместо чтения файла он использовал эту конечную точку для получения необходимых данных. Вот как будет выглядеть новый ассет:

```python
# src/dagster_testing/defs/assets/lesson_4.py
API_URL = "https://fake.com/population.json"


@dg.asset
def state_population_api() -> list[dict]:
    output = []
    try:
        response = requests.get(API_URL, params={"state": "ny"})
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

Приведённый код:

1. Запрашивает у воображаемого API данные штата "ny".
2. Извлекает JSON из ответа API.
3. Разбирает JSON и извлекает поля "name" и "population" для каждого города.
4. Возвращает данные в виде списка словарей.

Всё понятно, но как тестировать этот ассет, особенно учитывая, что API даже не существует?

## Mock-объекты

При написании тестов не всегда нужно подключаться к используемой внешней системе. Из соображений стоимости, времени, безопасности и по многим другим причинам обычно лучше изолировать внешние зависимости от модульных тестов, которые должны быстро и предсказуемо проверять код.

{% callout %}
> 💡 Можно использовать тесты, подключающиеся к реальным системам. Мы обсудим их в следующем уроке.
{% /callout %}

Чтобы обеспечить изоляцию кода Python, можно использовать mock-объекты из `unittest.mock`. Они позволяют заменять зависимости контролируемыми ответами. При использовании mock-объектов подумай:

1. Какой сервис нужно имитировать.
2. Как имитируемый сервис должен работать, чтобы удовлетворить требованиям теста.

Начнём с сервиса, который нужно заменить. В данном случае это API `fake.com`. Мы обращаемся к API через библиотеку Python `requests`, поэтому в тесте необходимо имитировать её работу.

Далее рассмотрим, что возвращает вызов API. Мы знаем структуру JSON, поэтому можно создать `pytest.fixture` с примером данных:

```python
# tests/test_lesson_4.py
@pytest.fixture
def example_response():
    return {
    "cities": [
        {
            "city_name": "New York",
            "city_population": 8804190,
        },
        {
            "city_name": "Buffalo",
            "city_population": 278349,
        },
    ],
}
```

Теперь нужно настроить функцию `get` в `requests`, чтобы она возвращала наш пример ответа. Воспользуемся [Mock](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock) для задания такого поведения:

```python
mock_response = Mock()
mock_response.json.return_value = example_response
mock_response.raise_for_status.return_value = None
```

Этот код создаёт mock-объект и задаёт для `json()` возвращаемое значение с примером ответа. Теперь можно перенести этот фрагмент в тест. Добавим к тестовой функции декоратор `@patch`, который временно заменяет указанный объект. В данном случае будет подменена функция `requests.get`.

```python
# tests/test_lesson_4.py
@patch("requests.get")
def test_state_population_api(mock_get, example_response):
    mock_response = Mock()
    mock_response.json.return_value = example_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = lesson_4.state_population_api()

    assert len(result) == 2
    assert result[0] == {
        "city": "New York",
        "population": 8804190,
    }
    mock_get.assert_called_once_with(lesson_4.API_URL, params={"state": "ny"})
```

Приведённый код:

1. Временно заменяет `requests.get`.
2. Использует подменённый объект как входной параметр вместе с фикстурой `example_response`.
3. Создаёт `Mock()` и задаёт возвращаемое значение `json()` равным `example_response`.
4. Задаёт для подменённого объекта `mock_get` возвращаемое значение с имитируемым ответом.
5. Выполняет ассет.
6. С помощью `assert` проверяет соответствие результата ассета ожиданиям.
7. Проверяет, что mock-объект был вызван с правильным URL и параметрами.

Тест по-прежнему можно запускать с помощью pytest.

```bash
> pytest tests/test_lesson_4.py::test_state_population_api
...
tests/test_lesson_4.py .                                                          [100%]
```

Тест полностью обходит API и возвращает наши тестовые данные.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
