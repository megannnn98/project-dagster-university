---
title: 'Урок 4: Возможности Dagster: автоматизация'
module: 'ai_driven_data_engineering'
lesson: '4'
---

# Возможности Dagster

Когда проект и ассеты готовы, можно использовать скилл для добавления автоматизации. Например, настроить ежедневный запуск исходных ассетов в 8:00 по восточному стандартному времени США (EST).

## Промпт

Попроси агента добавить автоматизацию для созданных ассетов, чтобы они выполнялись ежедневно в 8:00 EST:

```text {% obfuscated="true" %}
/dagster-expert Add a daily schedule that runs the raw assets every day at 8am EST.
```

Скилл направляет агента к абстракциям планирования Dagster (заданию, выбирающему ассеты, и расписанию) и размещению их в правильных файлах внутри `defs/`.

## Что будет добавлено

Агент:

1. Определит или переиспользует задание, выбирающее три исходных ассета (например, через `dg.define_asset_job` или существующее задание в `defs/jobs.py`).
```python {% obfuscated="true" %}
# /src/university/defs/schedules/daily_raw.py
raw_ingestion_job = dg.define_asset_job(
    name="raw_ingestion_job",
    selection=dg.AssetSelection.groups("raw"),
)
```
2. Добавит расписание ежедневного запуска этого задания в 8:00 EST.
```python {% obfuscated="true" %}
# /src/university/defs/schedules/daily_raw.py
daily_raw_schedule = dg.ScheduleDefinition(
    name="daily_raw_8am_est",
    job=raw_ingestion_job,
    cron_schedule="0 8 * * *",
    execution_timezone="America/New_York",
    description="Materialize all raw assets every day at 8 AM Eastern.",
    default_status=dg.DefaultScheduleStatus.RUNNING,
)
```

Скилл знает, где находятся задания и расписания (например, `defs/jobs.py`, `defs/schedules.py`), как включить их в `Definitions` и как использовать `dg scaffold`, если нужны новые файлы. Поэтому «добавь расписание» становится одним промптом, создающим согласованный код в нужных местах вместо разрозненных правок. При добавлении ассетов или расписаний повторное использование того же скилла и рабочего процесса с `dg` сохраняет порядок и предсказуемость проекта.

Затем расписание включается в определения расположения кода (например, в `definitions.py` или через `defs/__init__.py`), чтобы оно отображалось в интерфейсе Dagster и выполнялось с заданной периодичностью после включения. Это ещё одно преимущество структуры проектов Dagster, где `dg` обеспечивает автоматическую загрузку объектов проекта. Агенту требуется писать и учитывать меньше кода, а вероятность незаметной рассинхронизации в ходе разработки снижается.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
