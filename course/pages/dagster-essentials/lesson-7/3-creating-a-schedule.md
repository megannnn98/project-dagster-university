---
title: 'Урок 7: Создание расписания'
module: 'dagster_essentials'
lesson: '7'
---

# Создание расписания

Теперь, когда ты знаешь, из чего состоит расписание, создадим его. Для этого воспользуемся классом `ScheduleDefinition`.

Снова используем `dg` для создания каркаса расписаний. Сначала выполни:

```bash
dg scaffold defs dagster.schedule schedules.py
```

Будет создан файл `src/dagster_essentials/defs/schedules.py`, в который можно добавить следующий код расписания:

```python
# src/dagster_essentials/defs/schedules.py
import dagster as dg
from dagster_essentials.defs.jobs import trip_update_job

trip_update_schedule = dg.ScheduleDefinition(
    job=trip_update_job,
    cron_schedule="0 0 5 * *", # every 5th of the month at midnight
)
```

Разберём, что делает этот код:

1. Импортирует класс `ScheduleDefinition`.
2. Импортирует задание `trip_update_job` из модуля `jobs`.
3. Использует `ScheduleDefinition` для создания расписания, которое:
   - Связано с заданием `trip_update_job`.
   - Имеет выражение cron `0 0 5 * *`.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
