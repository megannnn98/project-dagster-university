---
title: 'Урок 8: Создание расписания с партициями по дате'
module: 'dagster_essentials'
lesson: '8'
---

# Создание расписания с партициями по дате

В предыдущем уроке ты создал задание `trip_update_job`, которое обновляет большинство ассетов. Для него настроено расписание обновления ассетов в полночь пятого числа каждого месяца.

Теперь, когда соответствующие ассеты разделены на партиции, можно изменить расписание так, чтобы получать только данные за последний месяц, не обновляя весь ассет. Это хорошая практика: обработка только новых данных экономит вычислительное время.

Сейчас `trip_update_job` в файле `jobs.py` должно выглядеть так:

```python
# src/dagster_essentials/defs/jobs.py
trips_by_week = dg.AssetSelection.assets("trips_by_week")

trip_update_job = dg.define_asset_job(
    name="trip_update_job",
    selection=dg.AssetSelection.all() - trips_by_week
)
```

Чтобы добавить партиционирование к заданию, внеси следующие изменения:

1. Импортируй `monthly_partition` из модуля `partitions`:

   ```python
   from dagster_essentials.defs.partitions import monthly_partition
   ```

2. Добавь к заданию параметр `partitions_def`, равный `monthly_partition`:

   ```python
   partitions_def=monthly_partition,
   ```

Теперь задание должно выглядеть так:

```python
# src/dagster_essentials/defs/jobs.py
import dagster as dg
from dagster_essentials.defs.partitions import monthly_partition

trips_by_week = dg.AssetSelection.assets("trips_by_week")

trip_update_job = dg.define_asset_job(
    name="trip_update_job",
    partitions_def=monthly_partition, # partitions added here
    selection=dg.AssetSelection.all() - trips_by_week
)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
