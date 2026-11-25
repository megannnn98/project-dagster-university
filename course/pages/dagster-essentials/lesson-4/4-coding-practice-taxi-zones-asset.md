---
title: 'Урок 4: Практика: создание ассета taxi_zones'
module: 'dagster_essentials'
lesson: '4'
---

# Практика: создание ассета taxi_zones

Применим полученные знания о зависимостях между ассетами, чтобы потренироваться создавать ассет с зависимостями.

В уроке 3 ты создал ассет `taxi_zones_file`, скачивающий CSV с данными о зонах такси Нью-Йорка.

Теперь создай ассет `taxi_zones`, использующий файл, созданный ассетом `taxi_zones_file`, для создания таблицы `zones` в базе DuckDB. В новой таблице должно быть четыре столбца:

- `zone_id` — переименованный столбец `LocationID`.
- `zone`.
- `borough`.
- `geometry` — переименованный столбец `the_geom`.

---

## Проверь свою работу

Созданный ассет должен выглядеть примерно как следующий код. Нажми **View answer**, чтобы посмотреть ответ.

**Если есть различия**, сравни свой код с ассетом ниже и внеси необходимые изменения: в следующих уроках этот ассет будет использоваться в таком виде.

```python {% obfuscated="true" %}
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(
    deps=["taxi_zones_file"]
)
def taxi_zones() -> None:
    query = f"""
        create or replace table zones as (
            select
                LocationID as zone_id,
                zone,
                borough,
                the_geom as geometry
            from '{constants.TAXI_ZONES_FILE_PATH}'
        );
    """

    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={
            "database": os.getenv("DUCKDB_DATABASE"),
        },
        max_retries=10,
    )
    conn.execute(query)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
