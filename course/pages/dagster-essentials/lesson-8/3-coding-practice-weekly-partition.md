---
title: 'Урок 8: Практика: создание недельной партиции'
module: 'dagster_essentials'
lesson: '8'
---

# Практика: создание недельной партиции

Чтобы закрепить изученное, создай `weekly_partition` с помощью `WeeklyPartitionsDefinition` Dagster, используя те же начальную и конечную даты.

---

## Проверь свою работу

Созданное определение партиций должно выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Если есть различия**, сравни свой код с определением ниже и внеси изменения: в следующих уроках оно будет использоваться в таком виде.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/partitions.py
import dagster as dg
from dagster_essentials.defs.assets import constants

start_date = constants.START_DATE
end_date = constants.END_DATE

weekly_partition = dg.WeeklyPartitionsDefinition(
    start_date=start_date,
    end_date=end_date
)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
