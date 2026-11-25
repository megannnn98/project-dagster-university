---
title: "Урок 6: Создание инкрементальной модели"
module: 'dagster_dbt'
lesson: '6'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Создание инкрементальной модели

Партиции расширяют возможности инкрементальных моделей. Сначала напишем инкрементальную модель dbt, затем настроим её партиционирование через Dagster.

Модель будет вычислять статистику поездок на такси в Нью-Йорке. Ежедневно пересчитывать всю историю дорого из-за объёма данных и стоимости вычисления некоторых метрик, поэтому используем инкрементальную материализацию.

В проекте dbt создайте `daily_metrics.sql` в каталоге `src/dagster_and_dbt/analytics/models/marts` и добавьте:

```sql
{{
  config(
    materialized='incremental',
    unique_key='date_of_business'
  )
}}

with
    trips as (
        select *
        from {{ ref('stg_trips') }}
    ),
    daily_summary as (
        select
            date_trunc('day', pickup_datetime) as date_of_business,
            count(*) as trip_count,
            sum(duration) as total_duration,
            sum(duration) / count(*) as average_duration,
            sum(total_amount) as total_amount,
            sum(total_amount) / count(*) as average_amount,
            sum(case when duration > 30 then 1 else 0 end) / count(*) as pct_over_30_min
        from trips
        group by all
    )
select *
from daily_summary
{% if is_incremental() %}
    where date_of_business > (select max(date_of_business) from {{ this }})
{% endif %}
```

Рассмотрим условие инкрементальной обработки:

```jsx
{% if is_incremental() %}
    where date_of_business > (select max(date_of_business) from {{ this }})
{% endif %}
```

Такое условие `where` выбирает только даты позднее максимальной уже обработанной даты. Это распространённый подход, но он затрудняет повторную обработку исторических данных.

Мы настроим партиционирование и передадим dbt явные границы выбираемых записей. Например, при обработке диапазона Dagster с 1 по 22 января 2024 года модель должна выбирать данные только за заданный период. Для этого изменим условие фильтрации.
