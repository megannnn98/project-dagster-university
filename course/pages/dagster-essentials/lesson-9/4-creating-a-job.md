---
title: 'Урок 9: Создание задания'
module: 'dagster_essentials'
lesson: '9'
---

# Создание задания

Далее создай задание для материализации нового актива `adhoc_request`. Оно будет практически идентично заданиям из урока 7.

Открой файл `defs/jobs.py` и добавь следующие строки перед `trip_update_job`, чтобы создать задание для разовых запросов:

```python
# src/dagster_essentials/defs/jobs.py
adhoc_request = dg.AssetSelection.assets(["adhoc_request"])

adhoc_request_job = dg.define_asset_job(
    name="adhoc_request_job",
    selection=adhoc_request,
)
```

Также необходимо обновить существующее задание `trip_update_job`. Используемая в нём исходная выборка `AssetSelection.all()` выберет и новый актив `adhoc_request`, но нам это не нужно. Как и в случае исключения актива `trips_by_week`, исключим из выборки актив `adhoc_request`, как показано ниже:

```python
# src/dagster_essentials/defs/jobs.py
trip_update_job = dg.define_asset_job(
    name="trip_update_job",
    partitions_def=monthly_partition,
    selection=dg.AssetSelection.all() - trips_by_week - adhoc_request
)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
