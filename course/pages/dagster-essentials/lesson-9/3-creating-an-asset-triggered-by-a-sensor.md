---
title: 'Урок 9: Создание актива, запускаемого сенсором'
module: 'dagster_essentials'
lesson: '9'
---

# Создание актива, запускаемого сенсором

Теперь, когда определён способ настройки материализации актива, создадим актив для разовых отчётов.

1. Добавь следующие импорты в `defs/assets/requests.py`:

   ```python
   # src/dagster_essentials/defs/assets/requests.py
   import dagster as dg
   from dagster_duckdb import DuckDBResource

   import matplotlib.pyplot as plt

   from dagster_essentials.defs.assets import constants
   ```

2. Создай новый актив `adhoc_request` со следующими параметрами и зависимостями:

   1. `config` с аннотацией типа `AdhocRequestConfig`.
   2. Активы `taxi_zones` и `taxi_trips` в качестве зависимостей.
   3. `database` с аннотацией типа `DuckDBResource` для выполнения запросов к DuckDB.

   На данном этапе актив должен выглядеть так:

   ```python
   @dg.asset(
       deps=["taxi_zones", "taxi_trips"]
   )
   def adhoc_request(config: AdhocRequestConfig, database: DuckDBResource) -> None:
   ```

3. При сохранении отчёта в файл его имя должно быть похоже на имя запроса. В файле `defs/assets/constants.py` уже предусмотрен шаблон `REQUEST_DESTINATION_TEMPLATE_FILE_PATH`.

   Сформируй имя файла с помощью шаблона, удалив расширение `.json` из имени файла запроса:

   ```python
   file_path = constants.REQUEST_DESTINATION_TEMPLATE_FILE_PATH.format(config.filename.split('.')[0])
   ```

4. Далее напиши SQL-запрос, который:

   - Отфильтровывает поездки, начавшиеся за пределами указанного района или диапазона дат.
   - Агрегирует данные по дню недели и часу начала поездки.

     Например:

     ```python
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
     ```

5. Выполни запрос в DuckDB и сохрани результат в виде DataFrame. Значения конфигурации подставляются вместо заполнителей `?` как параметры запроса, а не форматируются внутри строки SQL. Поэтому содержимое запроса пользователя не может изменить структуру SQL-запроса:

   ```python
   with database.get_connection() as conn:
       results = conn.execute(
           query, [config.start_date, config.end_date, config.borough]
       ).fetch_df()
   ```

6. Теперь, когда данные запроса сохранены в переменной `results` как DataFrame, воспользуйся библиотекой Matplotlib для визуализации количества поездок по времени суток в указанном районе с разбивкой по дням недели:

   ```python
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
   ```

7. Наконец, сохрани отчёт в целевой файл, указанный в ранее объявленной переменной `file_path`:

   ```python
   plt.savefig(file_path)
   plt.close(fig)
   ```

Убедись, что файл `requests.py` выглядит как следующий код:

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

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
