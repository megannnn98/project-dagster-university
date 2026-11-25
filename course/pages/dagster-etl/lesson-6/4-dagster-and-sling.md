---
title: 'Урок 6: Dagster и Sling'
module: 'dagster_etl'
lesson: '6'
---

# Dagster и Sling

При определении ассетов с помощью Sling сначала нужно задать источник и назначение. В данном случае источник — Postgres, а назначение — наша база DuckDB.

Для определения источника и назначения воспользуемся `SlingConnectionResource`. Для исходного экземпляра Postgres используем параметры подключения из Docker Compose.

```python
# src/dagster_and_etl/defs/resources.py
import dagster as dg
from dagster_sling import SlingConnectionResource, SlingResource

source = SlingConnectionResource(
    name="MY_POSTGRES",
    type="postgres",
    host="localhost",
    port=5432,
    database="test_db",
    user="test_user",
    password="test_pass",
)
```

У назначения меньше параметров, поскольку достаточно указать путь к локальному файлу базы DuckDB:

```python
# src/dagster_and_etl/defs/resources.py
destination = SlingConnectionResource(
    name="MY_DUCKDB",
    type="duckdb",
    connection_string="duckdb:///var/tmp/duckdb.db",
)
```

Определив источник и назначение, объединим их в `SlingResource`:

```python
# src/dagster_and_etl/defs/resources.py
sling = SlingResource(
    connections=[
        source,
        destination,
    ]
)
```

Наконец, зарегистрируем `sling` через объект `Definitions`:

```python
# src/dagster_and_etl/defs/resources.py
@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "sling": sling,
        },
    )
```

## YAML-конфигурация репликации

Подключения настроены, но ещё нужно определить, что именно мы реплицируем. Sling использует для этого YAML-файл репликации. Он определяет, какое подключение является источником, а какое — назначением:

```yaml
source: MY_POSTGRES
target: MY_DUCKDB
```

Ещё важнее решить, какие таблицы реплицировать из Postgres в DuckDB. Нам нужны только таблицы `data.customers`, `data.products` и `data.orders`, поэтому укажем их в `streams`.

```yaml
defaults:
  mode: full-refresh

  object: "{stream_schema}_{stream_table}"

streams:
  data.customers:
  data.products:
  data.orders:
```

Так мы настроим репликацию трёх таблиц в DuckDB.

## Ассеты Sling

Теперь можно сгенерировать ассеты Dagster. Поскольку мы уже выполнили большую часть работы, определив источник и назначение в `SlingResource` и параметры репликации в `replication.yaml`, Dagster может автоматически сгенерировать ассеты с помощью декоратора `sling_assets`:

```python
# src/dagster_and_etl/defs/assets.py
import dagster as dg
from dagster_sling import SlingResource, sling_assets

replication_config = dg.file_relative_path(__file__, "sling_replication.yaml")


@sling_assets(replication_config=replication_config)
def postgres_sling_assets(context, sling: SlingResource):
    yield from sling.replicate(context=context).fetch_column_metadata()
```

Это всё, что необходимо. Теперь при запуске `dg dev` на графе ассетов появится шесть новых ассетов.

Сначала идут три исходных ассета, представляющих необработанные таблицы в Postgres (customers, products, orders). С каждым из этих источников связан соответствующий ассет Dagster.

## Проверка данных

Чтобы убедиться, что всё загрузилось правильно, подключись к базе DuckDB с помощью [DuckDB CLI](https://duckdb.org/docs/stable/clients/cli/overview.html) и выполни запрос к только что созданной таблице.

```bash
> duckdb data/staging/data.duckdb
D SELECT * FROM data_customers;
┌─────────────┬────────────┬───────────┬───────────────────────────┐
│ customer_id │ first_name │ last_name │           email           │
│    int32    │  varchar   │  varchar  │          varchar          │
├─────────────┼────────────┼───────────┼───────────────────────────┤
│           1 │ Alice      │ Johnson   │ alice.johnson@example.com │
│           2 │ Bob        │ Smith     │ bob.smith@example.com     │
│           3 │ Charlie    │ Lee       │ charlie.lee@example.com   │
└─────────────┴────────────┴───────────┴───────────────────────────┘
```

Также можно посмотреть таблицы `data_products` или `data_orders`.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
