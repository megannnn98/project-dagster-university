---
title: 'Дополнительный раздел: Метаданные ассета в формате Markdown'
module: 'dagster_essentials'
lesson: 'extra-credit'
---

# Метаданные ассета в формате Markdown

В уроке 9 ты создал ассет `adhoc_request`. При материализации ассет строит столбчатую диаграмму и сохраняет её в хранилище. Такой подход удобен, если нужно обратиться к диаграмме позже. Но что делать, если хочется увидеть результат сразу после материализации? С помощью метаданных диаграмму можно просматривать непосредственно в интерфейсе Dagster!

---

## Добавление метаданных к ассету

1. Открой файл `assets/requests.py`.

2. На данном этапе курса ассет `adhoc_request` должен выглядеть так:

   ```python
   # src/dagster_essentials/defs/assets/requests.py
   import dagster as dg
   from dagster_duckdb import DuckDBResource

   import matplotlib.pyplot as plt

   from dagster_essentials.defs.assets import constants

   class AdhocRequestConfig(dg.Config):
     filename: str
     borough: str
     start_date: str
     end_date: str

   @dg.asset(
       deps=["taxi_zones", "taxi_trips"]
   )
   def adhoc_request(config: AdhocRequestConfig, database: DuckDBResource) -> None:
       """
         The response to an request made in the `requests` directory.
         See `requests/README.md` for more information.
       """

       # strip the file extension from the filename, and use it as the output filename
       file_path = constants.REQUEST_DESTINATION_TEMPLATE_FILE_PATH.format(config.filename.split('.')[0])

       # count the number of trips that picked up in a given borough, aggregated by time of day and hour of day
       query = """
           select
             date_part('hour', pickup_datetime) as hour_of_day,
             date_part('dayofweek', pickup_datetime) as day_of_week_num,
             case date_part('dayofweek', pickup_datetime)
               when 0 then 'Sunday'
               when 1 then 'Monday'
               when 2 then 'Tuesday'
               when 3 then 'Wednesday'
               when 4 then 'Thursday'
               when 5 then 'Friday'
               when 6 then 'Saturday'
             end as day_of_week,
             count(*) as num_trips
           from trips
           left join zones on trips.pickup_zone_id = zones.zone_id
           where pickup_datetime >= ?
           and pickup_datetime < ?
           and pickup_zone_id in (
             select zone_id
             from zones
             where borough = ?
           )
           group by 1, 2
           order by 1, 2 asc
       """

       # pass the config values as query parameters, so they can't change the SQL itself
       with database.get_connection() as conn:
           results = conn.execute(
               query, [config.start_date, config.end_date, config.borough]
           ).fetch_df()

       fig, ax = plt.subplots(figsize=(10, 6))
        
       # Pivot data for stacked bar chart
       results_pivot = results.pivot(index="hour_of_day", columns="day_of_week", values="num_trips")
       results_pivot.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")

       ax.set_title(f"Number of trips by hour of day in {config.borough}, from {config.start_date} to {config.end_date}")
       ax.set_xlabel("Hour of Day")
       ax.set_ylabel("Number of Trips")
       ax.legend(title="Day of Week")

       plt.xticks(rotation=45)
       plt.tight_layout()

       plt.savefig(file_path)
       plt.close(fig)
   ```

3. Добавь импорт `base64` в начало файла:

   ```python
   import base64
   import dagster as dg
   ```

4. После последней строки ассета добавь следующий код:

   ```python
   with open(file_path, 'rb') as file:
       image_data = file.read()
   ```

5. Далее воспользуемся кодированием base64, чтобы встроить диаграмму в Markdown. После строки с `image_data` добавь следующий код:

   ```python
   base64_data = base64.b64encode(image_data).decode('utf-8')
   md_content = f"![Image](data:image/jpeg;base64,{base64_data})"
   ```

6. Наконец, вернём объект `MaterializeResult` с метаданными в качестве параметра:

   ```python
   return dg.MaterializeResult(
       metadata={
           "preview": dg.MetadataValue.md(md_content)
       }
   )
   ```

   Разберём, что происходит:

   1. Создаётся переменная `base64_data`.
   2. Функция `base64.b64encode` кодирует двоичные данные изображения (`image_data`) в формат base64.
   3. Затем закодированные данные изображения преобразуются в строку UTF-8 с помощью функции `decode`.
   4. Создаётся переменная `md_content`. Её значение — строка в формате Markdown со встроенным JPEG-изображением, представленным в base64.
   5. Чтобы добавить метаданные к ассету, возвращаем экземпляр `MaterializeResult`, передавая изображение в метаданных. В интерфейсе Dagster метаданные будут иметь метку `preview`.
   6. С помощью `MetadataValue.md` для `md_content` указывается тип Markdown. Это обеспечивает корректное отображение диаграммы в Dagster.

На этом этапе код ассета `adhoc_request` должен выглядеть так:

```python
# src/dagster_essentials/defs/assets/requests.py
import dagster as dg
from dagster_duckdb import DuckDBResource

import matplotlib.pyplot as plt
import base64

from dagster_essentials.defs.assets import constants

class AdhocRequestConfig(dg.Config):
    filename: str
    borough: str
    start_date: str
    end_date: str

@dg.asset(
    deps=["taxi_zones", "taxi_trips"]
)
def adhoc_request(config: AdhocRequestConfig, database: DuckDBResource) -> dg.MaterializeResult:
    """
      The response to an request made in the `requests` directory.
      See `requests/README.md` for more information.
    """

    # strip the file extension from the filename, and use it as the output filename
    file_path = constants.REQUEST_DESTINATION_TEMPLATE_FILE_PATH.format(config.filename.split('.')[0])

    # count the number of trips that picked up in a given borough, aggregated by time of day and hour of day
    query = """
        select
          date_part('hour', pickup_datetime) as hour_of_day,
          date_part('dayofweek', pickup_datetime) as day_of_week_num,
          case date_part('dayofweek', pickup_datetime)
            when 0 then 'Sunday'
            when 1 then 'Monday'
            when 2 then 'Tuesday'
            when 3 then 'Wednesday'
            when 4 then 'Thursday'
            when 5 then 'Friday'
            when 6 then 'Saturday'
          end as day_of_week,
          count(*) as num_trips
        from trips
        left join zones on trips.pickup_zone_id = zones.zone_id
        where pickup_datetime >= ?
        and pickup_datetime < ?
        and pickup_zone_id in (
          select zone_id
          from zones
          where borough = ?
        )
        group by 1, 2
        order by 1, 2 asc
    """

    # pass the config values as query parameters, so they can't change the SQL itself
    with database.get_connection() as conn:
        results = conn.execute(
            query, [config.start_date, config.end_date, config.borough]
        ).fetch_df()

    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Pivot data for stacked bar chart
    results_pivot = results.pivot(index="hour_of_day", columns="day_of_week", values="num_trips")
    results_pivot.plot(kind="bar", stacked=True, ax=ax, colormap="viridis")
    
    ax.set_title(f"Number of trips by hour of day in {config.borough}, from {config.start_date} to {config.end_date}")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Number of Trips")
    ax.legend(title="Day of Week")
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(file_path)
    plt.close(fig)

    with open(file_path, "rb") as file:
        image_data = file.read()

    base64_data = base64.b64encode(image_data).decode('utf-8')
    md_content = f"![Image](data:image/jpeg;base64,{base64_data})"

    return dg.MaterializeResult(
        metadata={
            "preview": dg.MetadataValue.md(md_content)
        }
    )
```

---

## Просмотр метаданных в интерфейсе Dagster

После всей проделанной работы посмотрим, как это выглядит в интерфейсе!

1. Перейди на страницу **Global Asset Lineage**.
2. Нажми **Reload definitions**.
3. После обновления кода метаданных смоделируй тик сенсора.

<!-- TODO: Add link to Thinkific sensors lesson here? -->

В правой части экрана ты увидишь `preview` — метку, заданную для диаграммы в формате Markdown:

![Страница Global Asset Lineage с выбранным ассетом adhoc_request](/images/dagster-essentials/extra-credit/ui-selected-adhoc-request-asset.png)

Чтобы отобразить диаграмму, нажми **\[Show Markdown]**:

![Диаграмма, отображаемая в результате материализации ассета adhoc_request](/images/dagster-essentials/extra-credit/ui-markdown-chart.png)

Также можно нажать **View in Asset Catalog**, чтобы просмотреть диаграмму.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
