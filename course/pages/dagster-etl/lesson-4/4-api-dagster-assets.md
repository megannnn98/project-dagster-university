---
title: 'Урок 4: Ассеты Dagster для API'
module: 'dagster_etl'
lesson: '4'
---

# Ассеты Dagster для API

Теперь, когда мы лучше понимаем, как организовать извлечение данных из API, можно приступить к написанию кода Dagster. Поскольку мы хотим запускать пайплайн для любой заданной даты, хорошим первым шагом будет создание конфигурации запуска (как в предыдущем уроке), позволяющей указывать целевую дату во время выполнения. Это даёт возможность запускать пайплайн вручную, автоматизировать ежедневную загрузку и при необходимости выполнять backfill исторических данных:

```python
import dagster as dg

class NasaDate(dg.Config):
    date: str
```

Поскольку конфигурации запуска Dagster построены на моделях Pydantic, можно использовать `field_validator`, чтобы убедиться, что переданная строка даты имеет правильный формат (например, `YYYY-MM-DD`). Это добавляет уровень валидации, помогающий обнаруживать проблемы до начала выполнения пайплайна:

```python
# src/dagster_and_etl/defs/assets.py
import datetime
from pydantic import field_validator

class NasaDate(dg.Config):
    date: str

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v):
        try:
            datetime.datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("event_date must be in 'YYYY-MM-DD' format")
        return v
```

## Ассет Dagster

Теперь, когда конфигурация запуска готова, определим ассеты Dagster. Первый ассет будет называться `asteroids`. Он воспользуется ранее определённым ресурсом `NASAResource`, чтобы извлечь данные об астероидах за определённый день. В данном случае — за предыдущий день относительно даты в конфигурации запуска.

Для корректного вызова API необходимо вычислить start_date и end_date на основе входной даты. Ассет вернёт список словарей, каждый из которых представляет астероид, наблюдавшийся в этот период:

```python {% obfuscated="true" %}
# src/dagster_and_etl/defs/assets.py
from dagster_and_etl.defs.resources import NASAResource

@dg.asset(
    kinds={"nasa"},
)
def asteroids(
    context: dg.AssetExecutionContext,
    config: NasaDate,
    nasa: NASAResource,
) -> list[dict]:
    anchor_date = datetime.datetime.strptime(config.date, "%Y-%m-%d")
    start_date = (anchor_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    return nasa.get_near_earth_asteroids(
        start_date=start_date,
        end_date=config.date,
    )
```

Теперь, когда данные получены из API, следующим шагом станет их загрузка в DuckDB. Один из подходов — выполнить оператор `INSERT` для каждой записи, но такой шаблон не подходит для OLAP-баз данных вроде DuckDB, оптимизированных для пакетной вставки, а не построчных операций.

Более эффективный метод, соответствующий предыдущему уроку, — записать данные в файл, а затем загрузить файл в DuckDB с помощью оператора `COPY` или аналогичного механизма пакетной загрузки.

Поэтому следующий ассет возьмёт список словарей, возвращённый API, и сохранит его в плоский файл (например, CSV). Чтобы упростить результат и не работать с глубоко вложенными структурами JSON, ограничимся следующими полями:

- id
- name
- absolute_magnitude_h
- is_potentially_hazardous_asteroid

```python {% obfuscated="true" %}
# src/dagster_and_etl/defs/assets.py
@dg.asset
def asteroids_file(
    context: dg.AssetExecutionContext,
    asteroids,
) -> Path:
    filename = "asteroid_staging"
    file_path = (
        Path(__file__).absolute().parent / f"../../../data/staging/{filename}.csv"
    )

    # Only load specific fields
    fields = [
        "id",
        "name",
        "absolute_magnitude_h",
        "is_potentially_hazardous_asteroid",
    ]

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()
        writer.writerows(
            {key: row[key] for key in fields if key in row} for row in asteroids
        )

    return file_path
```

Последний ассет будет очень похож на созданный в предыдущем уроке. Мы создадим таблицу в DuckDB с четырьмя выбранными полями и воспользуемся оператором `COPY` для загрузки данных из только что записанного файла. Такой подход использует возможности эффективной пакетной загрузки DuckDB и позволяет сохранить ассет простым и производительным. Повторно используя один и тот же шаблон, мы обеспечиваем согласованность ETL-пайплайнов независимо от источника — локального файла или внешнего API:

```python
# src/dagster_and_etl/defs/assets.py
@dg.asset(
    kinds={"duckdb"},
)
def duckdb_table(
    context: dg.AssetExecutionContext,
    database: DuckDBResource,
    asteroids_file,
) -> None:
    table_name = "raw_asteroid_data"
    with database.get_connection() as conn:
        table_query = f"""
            create table if not exists {table_name} (
                id varchar(10),
                name varchar(100),
                absolute_magnitude_h float,
                is_potentially_hazardous_asteroid boolean
            ) 
        """
        conn.execute(table_query)
        conn.execute(f"copy {table_name} from ?", [str(asteroids_file)])
```

Теперь можно выполнить пайплайн для конкретной даты.

## Проверка данных

Чтобы убедиться, что всё загрузилось правильно, подключись к базе данных DuckDB с помощью [DuckDB CLI](https://duckdb.org/docs/stable/clients/cli/overview.html) и выполни запрос к только что созданной таблице.

```bash
> duckdb data/staging/data.duckdb
D SELECT * FROM raw_asteroid_data;
┌─────────┬───────────────────────┬──────────────────────┬───────────────────────────────────┐
│   id    │         name          │ absolute_magnitude_h │ is_potentially_hazardous_asteroid │
│ varchar │        varchar        │        float         │              boolean              │
├─────────┼───────────────────────┼──────────────────────┼───────────────────────────────────┤
│ 2004034 │ 4034 Vishnu (1986 PA) │                18.49 │ true                              │
└─────────┴───────────────────────┴──────────────────────┴───────────────────────────────────┘
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
