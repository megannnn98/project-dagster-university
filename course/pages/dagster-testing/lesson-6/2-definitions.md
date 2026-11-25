---
title: 'Урок 6: Definitions'
module: 'dagster_testing'
lesson: '6'
---

# Definitions

Один из важнейших объектов проекта Dagster — `Definitions`. Он определяет все объекты, которые будут развёрнуты в твоём расположении кода. Если ты используешь `dg`, возможно, уже привык проверять корректность `Definitions` командой `dg check defs`.

Это хорошая привычка, и можно построить рабочие процессы (например, pre-commit-хуки), которые всегда выполняют эту проверку. Однако полезно также написать отдельный тест, который будет находиться рядом с остальными тестами Dagster.

К счастью, такой тест очень легко написать.

## Загрузка объекта Definitions

Декоратор `@dg.definitions` использует отложенное вычисление. Это означает, что определения загружаются только тогда, когда они нужны. Для загрузки можно использовать `dg.components.load_defs`.

Теперь напишем тест, проверяющий, что определения успешно загружаются.

```python
# tests/test_lesson_6.py
import dagster_testing.defs

def test_defs():
    assert dg.components.load_defs(dagster_testing.defs)
```

```bash
> pytest tests/test_lesson_6.py::test_def
...
tests/test_lesson_6.py .                                                          [100%]
```

Несмотря на простоту, этот тест обнаружит множество проблем проекта Dagster. Он проверяет, что все объекты могут успешно загружаться и что определённые зависимости между объектами удовлетворены (например, необходимый ассету ресурс присутствует). Если возникнет проблема при загрузке ассетов, проверок ассетов, заданий, ресурсов, расписаний или сенсоров в Definitions, тест её выявит.

Загрузку Definitions можно вынести в фикстуру, если нужно выполнять несколько тестов над определениями.

```python
# tests/test_lesson_6.py
@pytest.fixture()
def defs():
    return dg.Definitions.merge(dg.components.load_defs(dagster_testing.defs))

def test_defs(defs):
    assert defs
```

{% callout %}

💡 **Модульные тесты:** хотя этот тест обнаруживает множество проблем, всё равно нужны отдельные тесты, проверяющие, что ассеты и другие объекты Dagster __выполняются__ ожидаемым образом. Тест Definitions проверяет только корректность __загрузки__ объектов.

{% /callout %}

## Объекты Definitions

Объект `Definitions` содержит дополнительные методы доступа к различным содержащимся в нём объектам. Например, вместо прямого импорта ассетов можно получить их из Definitions. Получим ассет `squared` и протестируем его через Definitions.

```python
# tests/test_lesson_6.py
def test_square_asset(defs):
    _asset = defs.get_assets_def("squared")
    assert _asset(5) == 25
```

```bash
> pytest tests/test_lesson_6.py::test_square_asset
...
tests/test_lesson_6.py .                                                          [100%]
```

Обрати внимание: доступ к объектам Dagster отличается, когда у них явно задан ключ. Например, рассмотрим ассет `squared_key`.

```python
# src/dagster_testing/defs/assets/lesson_6.py
@dg.asset(key=["target", "main", "square_key"])
def squared_key(number: int):
    return number * number
```

Для доступа к нему нужно задать ключ с помощью `dg.AssetKey`.

```python
# tests/test_lesson_6.py
def test_square_key_asset(defs):
    _asset = defs.get_assets_def(dg.AssetKey(["target", "main", "square_key"]))
    assert _asset(5) == 25
```

## Компоненты

Доступ к объектам Dagster через объект `definitions` особенно полезен при работе с компонентами.

Поскольку компоненты обычно не предоставляют содержащиеся в них объекты Dagster в виде напрямую импортируемого кода, при написании тестов или выполнении операций с ассетами и заданиями, сгенерированными компонентами, следует загружать объект `definitions` и получать нужные объекты из него.

```python
# tests/test_lesson_6.py
def test_materialize_partition(defs, duckdb_resource):
    result = dg.materialize(
        assets=[
            defs.get_assets_def(dg.AssetKey(["target", "main", "stg_customers"])), # asset from dbt component
            defs.get_assets_def(dg.AssetKey(["target", "main", "stg_orders"])), # asset from dbt component
            defs.get_assets_def(dg.AssetKey(["target", "main", "stg_payments"])), # asset from dbt component
            assets.monthly_orders, # user defined component downstream of dbt
        ],
        resources={
            "duckdb": duckdb_resource,
        },
        partition_key="2024-01-01",
    )
    assert result.success
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
