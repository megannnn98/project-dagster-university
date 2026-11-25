---
title: "Урок 5: Создание ассетов, зависящих от моделей dbt"
module: 'dagster_dbt'
lesson: '5'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Создание ассетов, зависящих от моделей dbt

Вы загрузили модели dbt как ассеты Dagster и связали их с исходными ассетами. Но модель dbt не всегда завершает пайплайн: после неё может потребоваться построить график, обновить дашборд или отправить данные в Salesforce.

Создадим ассет Dagster, зависящий от модели dbt. Сначала рассчитаем метрики в dbt, затем построим по ним график на Python.

В агломерации Нью-Йорка есть три крупных аэропорта: JFK, LGA и EWR. Проверим, как аэропорт прибытия связан с конечным районом поездки. Например, сколько поездок в Куинс началось в LGA?

---

## Создание модели dbt

Определим модель, вычисляющую метрики по созданным ранее staging-моделям.

В каталоге `src/dagster_and_dbt/analytics/models`:

1. Создайте каталог `marts`.
2. Создайте в нём файл `location_metrics.sql`.
3. Добавьте следующий код:

    ```sql
    with
        trips as (
            select *
            from {{ ref('stg_trips') }}
        ),
        zones as (
            select *
            from {{ ref('stg_zones') }}
        ),
        trips_by_zone as (
            select
                pickup_zones.zone_name as zone,
                dropoff_zones.borough as destination_borough,
                pickup_zones.is_airport as from_airport,
                count(*) as trips,
                sum(trips.trip_distance) as total_distance,
                sum(trips.duration) as total_duration,
                sum(trips.total_amount) as fare,
                sum(case when duration > 30 then 1 else 0 end) as trips_over_30_min
            from trips
            left join zones as pickup_zones on trips.pickup_zone_id = pickup_zones.zone_id
            left join zones as dropoff_zones on trips.dropoff_zone_id = dropoff_zones.zone_id
            group by all
        )
    select *
    from trips_by_zone
    ```

4. В интерфейсе Dagster перезагрузите расположение кода.
5. Найдите и материализуйте новый ассет dbt `location_metrics`:

   ![Новый ассет dbt location_metrics в Dagster](/images/dagster-dbt/lesson-5/new-location-metrics-asset.png)

---

## Создание ассета Dagster

Создадим ассет, использующий столбцы `location_metrics` для отображения числа поездок из каждого аэропорта по районам назначения.

### Добавление константы

В конец `defs/assets/constants.py` добавьте строковую константу, задающую путь к графику:

```python
AIRPORT_TRIPS_FILE_PATH = get_path_for_env(os.path.join("data", "outputs", "airport_trips.png"))
``` 

Вспомогательная функция `get_path_for_env` определена в этом файле и не относится к API Dagster. Она понадобится в седьмом уроке при развёртывании проекта Dagster и dbt.

### Создание ассета airport_trips

1. Откройте `defs/assets/metrics.py`.
2. В конце файла определите функцию `airport_trips`. Она принимает существующий ресурс `database` типа `DuckDBResource` и возвращает `MaterializeResult` с метаданными:

    ```python
    def airport_trips(database: DuckDBResource) -> dg.MaterializeResult:
    ```

3. Добавьте декоратор ассета, указав модель `location_metrics` как зависимость:

    ```python
    @dg.asset(
        deps=["location_metrics"],
    )
    def airport_trips(database: DuckDBResource) -> dg.MaterializeResult:
    ```

   **Примечание:** Dagster рассматривает модели dbt как обычные ассеты, поэтому зависимость задаётся тем же способом.

4. Заполните тело функции: запросите данные, постройте график, сохраните изображение в файл и добавьте предпросмотр в метаданные. Получится следующий ассет:

   ```python
   # src/dagster_and_dbt/defs/assets/metrics.py
   @dg.asset(
       deps=["location_metrics"],
   )
   def airport_trips(database: DuckDBResource) -> dg.MaterializeResult:
       """
           A chart of where trips from the airport go
       """

       query = """
           select
               zone,
               destination_borough,
               trips
           from location_metrics
           where from_airport
       """
       with database.get_connection() as conn:
           airport_trips = conn.execute(query).fetch_df()

       # Plot bars
       fig, ax = plt.subplots(figsize=(10, 6))

       # Group data by destination_borough and plot the bar chart
       airport_trips.groupby(['zone', 'destination_borough']).sum()['trips'].unstack().plot(
           kind='bar', stacked=True, ax=ax
       )

       # Customize the plot
       ax.set_xlabel("Zone")
       ax.set_ylabel("Number of Trips")
       ax.set_title("Trips from Airport by Destination Borough")
       ax.legend(title="Destination Borough")

       # Save the image
       plt.savefig(constants.AIRPORT_TRIPS_FILE_PATH, format="png", bbox_inches="tight")
       plt.close(fig)

       # Convert the image data to base64
       with open(constants.AIRPORT_TRIPS_FILE_PATH, "rb") as file:
           image_data = file.read()

        # Convert the image data to base64
       base64_data = base64.b64encode(image_data).decode('utf-8')
       md_content = f"![Image](data:image/jpeg;base64,{base64_data})"

       return dg.MaterializeResult(
           metadata={
               "preview": dg.MetadataValue.md(md_content)
           }
       )
   ```

5. Перезагрузите расположение кода. Новый ассет `airport_trips` появится в группе `metrics`. Граф покажет его зависимость от ассета dbt `location_metrics`:

   ![Ассет airport_trips в графе Dagster](/images/dagster-dbt/lesson-5/airport-trips-asset.png)

---

## Типичные метаданные MaterializeResult

Ассет `airport_trips` вернул предпросмотр графика, но `MaterializeResult` принимает любые метаданные, полезные для наблюдаемости:

| Назначение | Тип MetadataValue | Пример |
|---|---|---|
| Число строк | `MetadataValue.int()` | `{"row_count": dg.MetadataValue.int(n_rows)}` |
| Предпросмотр таблицы в Markdown | `MetadataValue.md()` | `{"preview": dg.MetadataValue.md(df.to_markdown())}` |
| График или изображение | `MetadataValue.md()` | URI данных в base64, как в примере выше |
| Путь к выходному файлу | `MetadataValue.path()` | `{"output": dg.MetadataValue.path(file_path)}` |
| Внешняя ссылка | `MetadataValue.url()` | `{"dashboard": dg.MetadataValue.url(url)}` |

В одном словаре `metadata` можно объединять несколько значений:

```python
return dg.MaterializeResult(
    metadata={
        "row_count": dg.MetadataValue.int(n_rows),
        "preview": dg.MetadataValue.md(df.head(10).to_markdown()),
    }
)
```

Сами ассеты dbt не используют `MaterializeResult`: при вызове `yield from dbt.cli([...]).stream()` интеграция `dagster-dbt` автоматически передаёт события материализации каждой модели. `MaterializeResult` нужен для написанных вами ассетов Dagster на Python, например `airport_trips`, расположенных ниже по графу зависимостей.
