---
title: 'Урок 3: Практика: создание актива taxi_zones_file'
module: 'dagster_essentials'
lesson: '3'
---

# Практика: создание актива taxi_zones_file

Чтобы закрепить изученное, создай в `trips.py` актив, который:

- Называется `taxi_zones_file`. Этот актив будет содержать уникальный идентификатор и название каждой части Нью-Йорка, выделенной в отдельную зону такси.
- Использует библиотеку `requests` для получения данных [NYC Taxi Zones](https://opendata.cityofnewyork.us/) по [этой ссылке](https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv): `https://community-engineering-artifacts.s3.us-west-2.amazonaws.com/dagster-university/data/taxi_zones.csv`
- Сохраняет данные в формате CSV в файл `data/raw/taxi_zones.csv`. Этот путь уже задан в `constants.TAXI_ZONES_FILE_PATH`.

---

## Проверь свою работу

Созданный актив должен выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Если есть различия**, сравни свой код с активом ниже и внеси необходимые изменения: в следующих уроках этот актив будет использоваться в таком виде.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/trips.py
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

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
