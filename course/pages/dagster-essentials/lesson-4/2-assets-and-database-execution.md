---
title: 'Урок 4: Ассеты и вычисления в базе данных'
module: 'dagster_essentials'
lesson: '4'
---

# Ассеты и вычисления в базе данных

В конце предыдущего урока ты создал два независимых ассета: `taxi_trips_file` в ходе урока и `taxi_zones_file` в разделе **Практическое задание**. В этом разделе ты создашь дополнительные ассеты, зависящие от них.

Прежде чем выполнять какие-либо операции с этими файлами, загрузим их в базу данных для эффективной обработки и хранения. К счастью, в исходном шаблоне проекта уже установлена DuckDB.

DuckDB обладает рядом возможностей, упрощающих загрузку данных, например позволяет выполнять запросы непосредственно к файлам. Чтобы загрузить файл `taxi_trips` в базу DuckDB, можно выполнить следующий SQL-запрос:

```sql
create or replace table trips as (
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
```

Пока не беспокойся о том, как выполнить этот запрос. Мы разберём это в следующем разделе.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
