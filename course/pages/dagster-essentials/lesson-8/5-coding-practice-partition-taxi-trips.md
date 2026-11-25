---
title: 'Урок 8: Практика: партиционирование актива taxi_trips'
module: 'dagster_essentials'
lesson: '8'
---

# Практика: партиционирование актива taxi_trips

Чтобы закрепить изученное, раздели актив `taxi_trips` на месячные партиции, следуя рекомендациям:

- Поскольку файл Parquet за месяц может содержать исторические данные за пределами этого месяца, рекомендуется партиционировать данные по месяцу файла Parquet, а не по месяцу поездки.

- При материализации каждой партиции добавляй новые данные в таблицу `taxi_trips`.

- Для удобства добавь столбец `partition_date`, указывающий, из какой партиции была добавлена запись.

  {% callout %}
  Из-за нового столбца `partition_date` потребуется удалить существующую учебную таблицу `taxi_trips`. В интерактивном интерпретаторе Python или отдельном скрипте выполни:

  ```
  import duckdb
  conn = duckdb.connect(database="data/staging/data.duckdb")
  conn.execute("drop table trips;")
  ```
  {% /callout %}

- Поскольку после материализации первой партиции таблица `taxi_trips` уже будет существовать, SQL-запрос потребуется изменить.

- В этом активе необходимо выполнить три действия:
  - Создать таблицу `taxi_trips`, если она ещё не существует.
  - Удалить старые данные соответствующей `partition_date`, чтобы избежать дублирования при backfill.
  - Добавить новые записи из файла Parquet за месяц.

---

## Проверь свою работу

Обновлённый актив должен выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Если есть различия**, сравни свой код с активом ниже и внеси изменения: в следующих уроках он будет использоваться в таком виде.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg
from dagster_duckdb import DuckDBResource
from dagster_essentials.defs.partitions import monthly_partition

@dg.asset(
  deps=["taxi_trips_file"],
  partitions_def=monthly_partition,
)
def taxi_trips(context: dg.AssetExecutionContext, database: DuckDBResource) -> None:
  """
    The raw taxi trips dataset, loaded into a DuckDB database, partitioned by month.
  """

  partition_date_str = context.partition_key
  month_to_fetch = partition_date_str[:-3]

  create_query = """
    create table if not exists trips (
      vendor_id integer, pickup_zone_id integer, dropoff_zone_id integer,
      rate_code_id double, payment_type integer, dropoff_datetime timestamp,
      pickup_datetime timestamp, trip_distance double, passenger_count double,
      total_amount double, partition_date varchar
    );
  """

  delete_query = "delete from trips where partition_date = ?;"

  insert_query = """
    insert into trips
    select
      VendorID, PULocationID, DOLocationID, RatecodeID, payment_type, tpep_dropoff_datetime,
      tpep_pickup_datetime, trip_distance, passenger_count, total_amount, ? as partition_date
    from read_parquet(?);
  """

  with database.get_connection() as conn:
      conn.execute(create_query)
      conn.execute(delete_query, [month_to_fetch])
      conn.execute(
          insert_query,
          [month_to_fetch, constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)],
      )
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
