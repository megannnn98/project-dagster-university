---
title: 'Урок 7: Практика: создание weekly_update_job'
module: 'dagster_essentials'
lesson: '7'
---

# Практика: создание weekly_update_job

Чтобы закрепить изученное, добавь в `src/dagster_essentials/defs/jobs.py` задание, материализующее актив `trips_by_week`.

---

## Проверь свою работу

Созданное задание должно выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Если есть различия**, сравни свой код с заданием ниже и внеси изменения: в следующих уроках это задание будет использоваться в таком виде.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/jobs.py
import dagster as dg

trips_by_week = dg.AssetSelection.assets(["trips_by_week"])

weekly_update_job = dg.define_asset_job(
    name="weekly_update_job",
    selection=trips_by_week,
)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
