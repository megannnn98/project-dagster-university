---
title: 'Урок 6: Практика: рефакторинг ассетов для использования ресурсов'
module: 'dagster_essentials'
lesson: '6'
---

# Практика: рефакторинг ассетов для использования ресурсов

Следующие ассеты используют базу данных DuckDB:

- `taxi_zones`
- `manhattan_stats`
- `trips_by_week`

Обнови эти ассеты, чтобы они использовали `DuckDBResource`.

---

## Проверь свою работу

Обновлённые ассеты должны выглядеть примерно как в следующих фрагментах кода. Нажми **View answer**, чтобы посмотреть ответы.

В оставшейся части курса мы будем предполагать, что твой код выглядит как приведённый ниже. Если твой вариант отличается от предоставленных решений, приведи код в соответствие с ответами и повторно материализуй эти ассеты, чтобы подготовиться к следующей части урока.

### В файле assets/trips.py:

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(
    deps=["taxi_zones_file"],
)
def taxi_zones(database: DuckDBResource) -> None:
    """
      The raw taxi zones dataset, loaded into a DuckDB database.
    """

    query = f"""
      create or replace table zones as (
        select
          LocationID as zone_id,
          zone,
          borough,
          the_geom as geometry
        from '{constants.TAXI_ZONES_FILE_PATH}'
      );
    """

    with database.get_connection() as conn:
        conn.execute(query)
```

### В файле assets/metrics.py:

Обнови импорты в файле `defs/assets/metrics.py` следующим образом:

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/metrics.py
from datetime import datetime, timedelta

import dagster as dg
from dagster_duckdb import DuckDBResource
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from dagster_essentials.defs.assets import constants
```

Обнови ассет `manhattan_stats`:

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/metrics.py
@dg.asset(
    deps=["taxi_trips", "taxi_zones"]
)
def manhattan_stats(database: DuckDBResource) -> None:
    """
      Metrics on taxi trips in Manhattan
    """

    query = """
      select
        zones.zone,
        zones.borough,
        zones.geometry,
        count(1) as num_trips,
      from trips
      left join zones on trips.pickup_zone_id = zones.zone_id
      where geometry is not null
      group by zone, borough, geometry
    """

    with database.get_connection() as conn:
        trips_by_zone = conn.execute(query).fetch_df()

    trips_by_zone["geometry"] = gpd.GeoSeries.from_wkt(trips_by_zone["geometry"])
    trips_by_zone = gpd.GeoDataFrame(trips_by_zone)

    with open(constants.MANHATTAN_STATS_FILE_PATH, 'w') as output_file:
        output_file.write(trips_by_zone.to_json())
```

Обнови ассет `trips_by_week`:

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/metrics.py
@dg.asset(
    deps = ["taxi_trips"]
)
def trips_by_week(database: DuckDBResource) -> None:

    current_date = datetime.strptime("2023-01-01", constants.DATE_FORMAT)
    end_date = datetime.now()

    result = pd.DataFrame()

    while current_date < end_date:
        current_date_str = current_date.strftime(constants.DATE_FORMAT)
        query = """
          select
            vendor_id, total_amount, trip_distance, passenger_count
          from trips
          where pickup_datetime >= ? and pickup_datetime < ?::date + interval '1 week'
        """

        with database.get_connection() as conn:
            data_for_week = conn.execute(
                query, [current_date_str, current_date_str]
            ).fetch_df()

        aggregate = data_for_week.agg({
            "vendor_id": "count",
            "total_amount": "sum",
            "trip_distance": "sum",
            "passenger_count": "sum"
        }).rename({"vendor_id": "num_trips"}).to_frame().T # type: ignore

        aggregate["period"] = current_date

        result = pd.concat([result, aggregate])

        current_date += timedelta(days=7)

    # clean up the formatting of the dataframe
    result['num_trips'] = result['num_trips'].astype(int)
    result['passenger_count'] = result['passenger_count'].astype(int)
    result['total_amount'] = result['total_amount'].round(2).astype(float)
    result['trip_distance'] = result['trip_distance'].round(2).astype(float)
    result = result[["period", "num_trips", "total_amount", "trip_distance", "passenger_count"]]
    result = result.sort_values(by="period")

    result.to_csv(constants.TRIPS_BY_WEEK_FILE_PATH, index=False)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
