---
title: 'Дополнительный раздел: Практика: добавление метаданных в taxi_zones_file'
module: 'dagster_essentials'
lesson: 'extra-credit'
---

# Практика: добавление метаданных в taxi_zones_file

Чтобы закрепить изученное, добавь количество записей в метаданные ассета `taxi_zones_file`.

---

## Проверь свою работу

Созданные метаданные должны выглядеть примерно как код, скрытый под переключателем **View answer**. Нажми на него, чтобы открыть ответ.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg

@dg.asset(
    group_name="raw_files",
)
def taxi_zones_file() -> dg.MaterializeResult:
    """
      The raw CSV file for the taxi zones dataset. Sourced from the NYC Open Data portal.
    """
    raw_taxi_zones = requests.get(
        "https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv"
    )

    with open(constants.TAXI_ZONES_FILE_PATH, "wb") as output_file:
        output_file.write(raw_taxi_zones.content)
    num_rows = len(pd.read_csv(constants.TAXI_ZONES_FILE_PATH))

    return dg.MaterializeResult(
        metadata={
            'Number of records': dg.MetadataValue.int(num_rows)
        }
    )
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
