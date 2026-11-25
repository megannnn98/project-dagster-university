---
title: 'Урок 6: Использование ресурсов в ассетах'
module: 'dagster_essentials'
lesson: '6'
---

# Использование ресурсов в ассетах

Теперь, когда ресурс определён, отрефакторим ассет `taxi_trips`, чтобы использовать его.

Для начала сравним код до и после изменения.

---

## До добавления ресурса

Следующий код показывает, как сейчас выглядит ассет `taxi_trips` без использования ресурса:

```python
# src/dagster_essentials/defs/assets/trips.py
import requests
import duckdb
import os
from dagster_essentials.defs.assets import constants
import dagster as dg

... # other assets

@dg.asset(
    deps=["taxi_trips_file"],
)
def taxi_trips() -> None:
    query = """
        create or replace table taxi_trips as (
          select
            VendorID as vendor_id,
            PULocationID as pickup_zone_id,
            DOLocationID as dropoff_zone_id,
            RatecodeID as rate_code_id,
            payment_type as payment_type,
            tpep_dropoff_datetime as dropoff_datetime,
            tpep_pickup_datetime as pickup_datetime,
            trip_distance as trip_distance,
            passenger_count as passenger_count,
            total_amount as total_amount
          from 'data/raw/taxi_trips_2023-03.parquet'
        );
    """

    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={
            "database": os.getenv("DUCKDB_DATABASE"),
        },
        max_retries=10,
    )
    conn.execute(query)
```

---

## После добавления ресурса

После добавления ресурса ассет `taxi_trips` выглядит следующим образом.

```python
# src/dagster_essentials/defs/assets/trips.py
import requests
from dagster_duckdb import DuckDBResource
from dagster_essentials.defs.assets import constants
import dagster as dg

... # other assets

@dg.asset(
    deps=["taxi_trips_file"],
)
def taxi_trips(database: DuckDBResource) -> None:
    query = """
        create or replace table taxi_trips as (
          select
            VendorID as vendor_id,
            PULocationID as pickup_zone_id,
            DOLocationID as dropoff_zone_id,
            RatecodeID as rate_code_id,
            payment_type as payment_type,
            tpep_dropoff_datetime as dropoff_datetime,
            tpep_pickup_datetime as pickup_datetime,
            trip_distance as trip_distance,
            passenger_count as passenger_count,
            total_amount as total_amount
          from 'data/raw/taxi_trips_2023-03.parquet'
        );
    """

    with database.get_connection() as conn:
        conn.execute(query)
```

Чтобы отрефакторить `taxi_trips` для использования ресурса `database`, необходимо было:

1. Заменить импорт `duckdb` на `from dagster_duckdb import DuckDBResource`, чтобы добавить аннотации типов в проект Dagster.
2. Обновить определение функции ассета `taxi_trips`, добавив параметр `database: DuckDBResource`. Эта аннотация типа нужна, чтобы Dagster понимал, что зависимость является ресурсом, а не ассетом.
3. Заменить строки, устанавливающие подключение к DuckDB и выполняющие запрос:

   ```python
   conn = backoff(
       fn=duckdb.connect,
       retry_on=(RuntimeError, duckdb.IOException),
       kwargs={
           "database": os.getenv("DUCKDB_DATABASE"),
       },
       max_retries=10,
   )
   conn.execute(query)
   ```

   На следующие строки, использующие ресурс `database`:

   ```python
   with database.get_connection() as conn:
       conn.execute(query)
   ```

   Обрати внимание, что больше не нужно использовать функцию `backoff`. Ресурс Dagster `DuckDBResource` берёт эту функциональность на себя.

---

## Перед продолжением

Прежде чем двигаться дальше, убедись, что ты:

1. Обновил файл `defs/assets/trips.py`, добавив отрефакторенный код ассета `taxi_trips`.
2. Перезагрузил определения в интерфейсе Dagster.
3. Повторно материализовал ассет `taxi_trips`.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
