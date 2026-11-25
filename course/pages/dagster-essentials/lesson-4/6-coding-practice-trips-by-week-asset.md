---
title: 'Урок 4: Практика: создание ассета trips_by_week'
module: 'dagster_essentials'
lesson: '4'
---

# Практика: создание ассета trips_by_week

Чтобы закрепить изученное, создай в файле `metrics.py` ассет с именем `trips_by_week`. Он должен создавать CSV-файл, который:

- Сохраняется по пути `constants.TRIPS_BY_WEEK_FILE_PATH`.
- Имеет следующую схему:
  - `period` — строка, представляющая воскресенье, с которого начинается неделя агрегации, например `2023-03-05`.
  - `num_trips` — общее количество поездок, начавшихся на этой неделе.
  - `passenger_count` — общее количество пассажиров такси за эту неделю.
  - `total_amount` — суммарная выручка от поездок за эту неделю.
  - `trip_distance` — суммарное расстояние в милях всех поездок за эту неделю.

{% callout %}

> 💡 **Дополнительное задание!** Если хочешь усложнить задачу, учти следующее ограничение:
> Представь, что все данные `trips` не помещаются в оперативную память, а данные за одну неделю помещаются без проблем. Как организовать функцию ассета с учётом этого ограничения?

{% /callout %}

---

## Подсказки

- Всё необходимое для решения задачи о Dagster уже было рассмотрено.
- Есть много способов решить задачу, например выполнить вычисления в базе данных или агрегировать DataFrame.
- Дополнительные импорты не обязательны, но можно импортировать всё необходимое.
- Для удобства и учёта проблем с качеством данных можно жёстко задать даты начала и конца анализа в пределах имеющихся данных (например, с `2023-03-05` по `2023-04-01`).
- DuckDB поддерживает сравнение дат и добавление временных интервалов: `+ interval ‘1 week’`.

Числа могут не совпадать в точности, но результат может выглядеть следующим образом:

```shell
period,num_trips,total_amount,trip_distance,passenger_count
2023-03-05,679681,18495110.72,2358944.42,886486
2023-03-12,686461,19151177.45,2664123.87,905296
2023-03-19,640158,17908993.09,2330611.91,838066
```

---

## Проверь свою работу

Созданный ассет должен выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Примечание:** приведённое ниже решение — лишь один из многих способов выполнить задание. Твой вариант вполне может быть правильным и даже более производительным! Эта задача также сложнее, чем предыдущие примеры ассетов.

В оставшейся части курса мы будем предполагать, что твой код выглядит как приведённый ниже. Хотя это не самый качественный код, он достаточно гибок для расширения в одном из следующих разделов.

**Если есть различия**, сравни свой код с ассетом ниже, внеси изменения и повторно материализуй ассет, чтобы подготовиться к следующему уроку.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/metrics.py
from datetime import datetime, timedelta
from dagster_essentials.defs.assets import constants

import pandas as pd
import dagster as dg
from dagster._utils.backoff import backoff

@dg.asset(
    deps=["taxi_trips"]
)
def trips_by_week() -> None:
    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={
            "database": os.getenv("DUCKDB_DATABASE"),
        },
        max_retries=10,
    )

    current_date = datetime.strptime("2023-03-05", constants.DATE_FORMAT)
    end_date = datetime.strptime("2023-04-01", constants.DATE_FORMAT)

    result = pd.DataFrame()

    while current_date < end_date:
        current_date_str = current_date.strftime(constants.DATE_FORMAT)
        query = """
            select
                vendor_id, total_amount, trip_distance, passenger_count
            from trips
            where pickup_datetime >= ?::date
              and pickup_datetime < ?::date + interval '1 week'
        """

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
