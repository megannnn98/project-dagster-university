---
title: 'Урок 5: Рефакторинг API с dlt'
module: 'dagster_etl'
lesson: '5'
---

# Рефакторинг API с dlt

Далее можно перенастроить API-пайплайн с помощью dlt. Это более специализированная реализация, чем загрузка данных из CSV, поэтому функция `@dlt.source` будет содержать больше кода. Однако большую часть логики можно повторно использовать из предыдущего урока.

```python
# src/dagster_and_etl/defs/assets.py
@dlt.source
def nasa_neo_source(start_date: str, end_date: str, api_key: str):
    @dlt.resource
    def fetch_neo_data():
        url = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "api_key": api_key,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        for neo in data["near_earth_objects"][start_date]:
            neo_data = {
                "id": neo["id"],
                "name": neo["name"],
                "absolute_magnitude_h": neo["absolute_magnitude_h"],
                "is_potentially_hazardous": neo["is_potentially_hazardous_asteroid"],
            }

            yield neo_data

    return fetch_neo_data
```

Теперь с помощью dlt можно получать данные из API NASA за любой диапазон дат. Вместо декоратора `dlt_assets` можно также поместить этот код непосредственно в ассет dg. Затем обновим функцию `nasa_neo_source`, чтобы она использовала значения конфигурации запуска.

```python
# src/dagster_and_etl/defs/assets.py
@dg.asset
def dlt_nasa(context: dg.AssetExecutionContext, config: NasaDate):
    anchor_date = datetime.datetime.strptime(config.date, "%Y-%m-%d")
    start_date = (anchor_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    @dlt.source
    def nasa_neo_source():
        @dlt.resource
        def load_neo_data():
            url = "https://api.nasa.gov/neo/rest/v1/feed"
            params = {
                "start_date": start_date,
                "end_date": config.date,
                "api_key": os.getenv("NASA_API_KEY"),
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            for neo in data["near_earth_objects"][config.date]:
                neo_data = {
                    "id": neo["id"],
                    "name": neo["name"],
                    "absolute_magnitude_h": neo["absolute_magnitude_h"],
                    "is_potentially_hazardous": neo[
                        "is_potentially_hazardous_asteroid"
                    ],
                }

                yield neo_data

        return load_neo_data

    pipeline = dlt.pipeline(
        pipeline_name="nasa_neo_pipeline",
        destination=dlt.destinations.duckdb(os.getenv("DUCKDB_DATABASE")),
        dataset_name="nasa_neo",
    )

    load_info = pipeline.run(nasa_neo_source())

    return load_info
```

Такая реализация функции также позволяет легко добавить партиции, как и для любого другого ассета.

```python
# src/dagster_and_etl/defs/assets.py
@dg.asset(
    partitions_def=nasa_partitions_def,
    automation_condition=dg.AutomationCondition.on_cron("@daily"),
)
def dlt_nasa_partition(context: dg.AssetExecutionContext):
    anchor_date = datetime.datetime.strptime(context.partition_key, "%Y-%m-%d")
    start_date = (anchor_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    @dlt.source
    def nasa_neo_source():
        @dlt.resource
        def load_neo_data():
            url = "https://api.nasa.gov/neo/rest/v1/feed"
            params = {
                "start_date": start_date,
                "end_date": context.partition_key,
                "api_key": os.getenv("NASA_API_KEY"),
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            for neo in data["near_earth_objects"][context.partition_key]:
                neo_data = {
                    "id": neo["id"],
                    "name": neo["name"],
                    "absolute_magnitude_h": neo["absolute_magnitude_h"],
                    "is_potentially_hazardous": neo[
                        "is_potentially_hazardous_asteroid"
                    ],
                }

                yield neo_data

        return load_neo_data

    pipeline = dlt.pipeline(
        pipeline_name="nasa_neo_pipeline",
        destination=dlt.destinations.duckdb(os.getenv("DUCKDB_DATABASE")),
        dataset_name="nasa_neo",
    )

    load_info = pipeline.run(nasa_neo_source())

    return load_info
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
