---
title: 'Урок 8: Практика: партиционирование ассета trips_by_week'
module: 'dagster_essentials'
lesson: '8'
---

# Практика: партиционирование ассета trips_by_week

Чтобы закрепить изученное, обнови `weekly_update_job` и `trips_by_week`, разделив их на недельные партиции. Используй существующее определение `weekly_partition` из предыдущего практического задания.

---

## Проверь свою работу

Обновлённый ассет и задание должны выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Если есть различия**, сравни свой код с приведённым ниже и внеси изменения: в следующих уроках он будет использоваться в таком виде.

### В файле assets/metrics.py:

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/metrics.py
from dagster_essentials.defs.partitions import weekly_partition

@dg.asset(
    deps=["taxi_trips"],
    partitions_def=weekly_partition
)
def trips_by_week(context: dg.AssetExecutionContext, database: DuckDBResource) -> None:
    """
      The number of trips per week, aggregated by week.
    """

    period_to_fetch = context.partition_key

    # get all trips for the week
    query = """
        select vendor_id, total_amount, trip_distance, passenger_count
        from trips
        where pickup_datetime >= ?
            and pickup_datetime < ?::date + interval '1 week'
    """

    with database.get_connection() as conn:
        data_for_week = conn.execute(
            query, [period_to_fetch, period_to_fetch]
        ).fetch_df()

    aggregate = data_for_week.agg({
        "vendor_id": "count",
        "total_amount": "sum",
        "trip_distance": "sum",
        "passenger_count": "sum"
    }).rename({"vendor_id": "num_trips"}).to_frame().T # type: ignore

    # clean up the formatting of the dataframe
    aggregate["period"] = period_to_fetch
    aggregate['num_trips'] = aggregate['num_trips'].astype(int)
    aggregate['passenger_count'] = aggregate['passenger_count'].astype(int)
    aggregate['total_amount'] = aggregate['total_amount'].round(2).astype(float)
    aggregate['trip_distance'] = aggregate['trip_distance'].round(2).astype(float)
    aggregate = aggregate[["period", "num_trips", "total_amount", "trip_distance", "passenger_count"]]

    try:
        # If the file already exists, append to it, but replace the existing month's data
        existing = pd.read_csv(constants.TRIPS_BY_WEEK_FILE_PATH)
        existing = existing[existing["period"] != period_to_fetch]
        existing = pd.concat([existing, aggregate]).sort_values(by="period")
        existing.to_csv(constants.TRIPS_BY_WEEK_FILE_PATH, index=False)
    except FileNotFoundError:
        aggregate.to_csv(constants.TRIPS_BY_WEEK_FILE_PATH, index=False)
```

### В файле `jobs.py`:

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/jobs.py
import dagster as dg
from dagster_essentials.defs.partitions import weekly_partition

trips_by_week = dg.AssetSelection.assets("trips_by_week")

weekly_update_job = dg.define_asset_job(
    name="weekly_update_job",
    partitions_def=weekly_partition,
    selection=trips_by_week,
)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
