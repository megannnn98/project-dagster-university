---
title: 'Дополнительный раздел: Метаданные определения — описания ассетов'
module: 'dagster_essentials'
lesson: 'extra-credit'
---

# Метаданные определения — описания ассетов

Если для ассета задано описание, оно отображается рядом с ним в интерфейсе Dagster. Добавить описание можно двумя способами:

- С помощью строк документации Python.
- С помощью параметра `description` декоратора ассета.

---

## Использование строк документации

По мере прохождения курса ты мог заметить, что ассеты содержат **строки документации (docstrings)**. [Строка документации Python](https://peps.python.org/pep-0257/) позволяет включить документацию о классе, модуле, функции или методе непосредственно в код. Хотя комментарии служат похожей цели, строки документации поддерживаются встроенными средствами Python, например [`help`](https://docs.python.org/3/library/functions.html#help).

Строку документации задают как первую инструкцию в определении объекта, заключая её в тройные кавычки (`"""`). Например:

```python
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg

@dg.asset
def taxi_zones_file() -> None:
    """
      The raw CSV file for the taxi zones dataset. Sourced from the NYC Open Data portal.
    """
    raw_taxi_zones = requests.get(
        "https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv"
    )

    with open(constants.TAXI_ZONES_FILE_PATH, "wb") as output_file:
        output_file.write(raw_taxi_zones.content)
```

---

## Использование параметра description

Другой способ добавить описание ассета — использовать параметр `description` декоратора ассета. **Примечание:** в интерфейсе Dagster такое описание имеет приоритет над строкой документации.

Например:

```python
# src/dagster_essentials/defs/assets/trips.py
import dagster as dg

@dg.asset(
    description="The raw CSV file for the taxi zones dataset. Sourced from the NYC Open Data portal."
)
def taxi_zones_file() -> None:
    """
      This will not show in the Dagster UI
    """
    raw_taxi_zones = requests.get(
        "https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv"
    )

    with open(constants.TAXI_ZONES_FILE_PATH, "wb") as output_file:
        output_file.write(raw_taxi_zones.content)
```

---

## Описания ассетов в интерфейсе Dagster

Теперь, когда ты знаешь, как задавать описания ассетов, посмотрим на них в интерфейсе Dagster.

{% table %}

- Страница ассетов

---

- {% width="60%" %}
  Для каждого ассета на вкладке **Lineage** описание отображается под ключом ассета.

{% /table %}

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
