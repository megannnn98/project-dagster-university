---
title: 'Урок 7: Практика: создание weekly_update_schedule'
module: 'dagster_essentials'
lesson: '7'
---

# Практика: создание weekly_update_schedule

Чтобы закрепить изученное, добавь в `src/dagster_essentials/defs/schedules.py` расписание, которое:

- Называется `weekly_update_schedule`.
- Материализует ассет `trips_by_week`.
- Выполняется каждый понедельник в полночь.

---

## Проверь свою работу

Созданное расписание должно выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Если есть различия**, сравни свой код с расписанием ниже и внеси изменения: в следующих уроках оно будет использоваться в таком виде.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/schedules.py
import dagster as dg

from dagster_essentials.defs.jobs import weekly_update_job

weekly_update_schedule = dg.ScheduleDefinition(
    job=weekly_update_job,
    cron_schedule="0 0 * * 1", # every Monday at midnight
)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
