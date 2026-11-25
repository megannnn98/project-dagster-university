---
title: 'Урок 4: Backfill данных из API'
module: 'dagster_etl'
lesson: '4'
---

# Backfill данных из API

Наш ETL-пайплайн настроен на постоянную загрузку новых данных из API. Но что насчёт исторических данных? Набор данных NASA охватывает несколько лет, и мы можем захотеть загрузить всю историю в наше хранилище данных.

Лучшая стратегия в этом случае — воспользоваться уже знакомой возможностью Dagster: партициями. Разделив данные по датам, можно использовать встроенную функциональность backfill в Dagster для запуска заданий, обрабатывающих определённые диапазоны дат. Это гораздо более удобный и управляемый подход, чем написание собственных скриптов или запуск огромного монолитного процесса, перебирающего результаты API за несколько лет.

Для начала определим дневные партиции пайплайна загрузки данных об астероидах. Это позволит выполнять backfill по одному дню и отслеживать прогресс за весь исторический период:

```python
nasa_partitions_def = dg.DailyPartitionsDefinition(
    start_date="2025-04-01",
)
```

Далее обновим ассет `asteroids`, чтобы он использовал партицию вместо конфигурации запуска. Для этого создадим отдельный ассет.

```python {% obfuscated="true" %}
# src/dagster_and_etl/defs/assets.py
@dg.asset(
    kinds={"nasa"},
    partitions_def=nasa_partitions_def,
)
def asteroids_partition(
    context: dg.AssetExecutionContext,
    nasa: NASAResource,
) -> list[dict]:
    anchor_date = datetime.datetime.strptime(context.partition_key, "%Y-%m-%d")
    start_date = (anchor_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    return nasa.get_near_earth_asteroids(
        start_date=start_date,
        end_date=context.partition_key,
    )
```

Этот ассет возвращает исходные данные об астероидах за дату своей партиции. В полноценном пайплайне нужно добавить нижестоящие ассеты, принимающие `asteroids_partition` на вход и записывающие данные сначала в файл, а затем в DuckDB, по аналогии с ассетами `asteroids_file` и `duckdb_table` из предыдущей части урока. Пока сосредоточимся на одном партиционированном ассете, чтобы показать, как работают backfill и повторные попытки с партициями.

## Ограничения частоты запросов

Ещё одна причина, по которой партиции хорошо подходят для backfill через API, — ограничения частоты запросов (rate limits). API, особенно возвращающие большие объёмы данных, часто устанавливают ограничения для предотвращения чрезмерной нагрузки на свои системы.

Хотя партиции не устраняют ограничения частоты запросов, они значительно упрощают отслеживание прогресса и восстановление после сбоев. Поскольку каждая партиция представляет отдельное временное окно (например, один день), при ошибке запроса из-за превышения лимита затрагивается только эта партиция. Это позволяет не терять результат всего задания и повторно запускать только завершившиеся ошибкой партиции вместо перезапуска всей загрузки. Кроме того, при необходимости проще ограничивать частоту или разносить запуски во времени.

Как мог бы выглядеть наш `NASAResource`, если добавить в него функциональность ограничения частоты запросов?

```python {% obfuscated="true" %}
# src/dagster_and_etl/defs/resources.py
import dagster as dg
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class NASAResource(dg.ConfigurableResource):
    api_key: str

    def get_near_earth_asteroids(self, start_date: str, end_date: str):
        url = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "api_key": self.api_key,
        }

        # Retries
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        resp = session.get(url, params=params)
        return resp.json()["near_earth_objects"][start_date]
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
