---
title: 'Урок 4: Ресурс API'
module: 'dagster_etl'
lesson: '4'
---

# Ресурс API

При работе с внешними API в Dagster часто лучше начать с создания ресурса. Ресурс предоставляет удобную абстракцию внешних сервисов, упрощая повторное использование логики API в нескольких ассетах. Кроме того, он упрощает тестирование и долгосрочное сопровождение, изолируя специфичную для API логику в одном чётко определённом интерфейсе.

Прежде чем писать код, рассмотрим характеристики API NeoWs (Near Earth Object Web Service). Базовый URL конечной точки:

```bash
https://api.nasa.gov/neo/rest/v1/feed
```

Эта конечная точка поддерживает три параметра запроса:

| Параметр | Тип | Значение по умолчанию | Описание |
| --- | --- | --- | --- |
| start_date | YYYY-MM-DD | отсутствует | Начальная дата поиска астероидов |
| end_date | YYYY-MM-DD | 7 дней после start_date | Конечная дата поиска астероидов |
| api_key | string | DEMO_KEY | Ключ api.nasa.gov для расширенных лимитов использования |

С учётом этой структуры полный запрос API может выглядеть так:

```bash
https://api.nasa.gov/neo/rest/v1/feed?start_date=2015-09-07&end_date=2015-09-08&api_key=DEMO_KEY
```

API вернёт большой JSON-ответ, содержащий различные поля метаданных. Для простоты сосредоточимся только на интересующей нас части — поле `near_earth_objects`. Оно содержит непосредственно данные об астероидах, сгруппированные по датам, и этого достаточно для нашего ETL-пайплайна.

## Реализация ресурса

Теперь, когда мы знаем конечную точку API и параметры вызова, напишем ресурс. Реализовать его можно по-разному, но мы остановимся на простой реализации.

Создадим ресурс `NASAResource`, инициализируемый нашим ключом API. Он будет предоставлять один метод: `get_near_earth_asteroids` с двумя параметрами (start_date, end_date), возвращающий разобранный JSON-ответ API.

Вот как это может выглядеть в файле `resources.py`:

```python {% obfuscated="true" %}
# src/dagster_and_etl/defs/resources.py
import dagster as dg
import requests


class NASAResource(dg.ConfigurableResource):
    api_key: str

    def get_near_earth_asteroids(self, start_date: str, end_date: str):
        url = "https://api.nasa.gov/neo/rest/v1/feed"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "api_key": self.api_key,
        }

        resp = requests.get(url, params=params)
        return resp.json()["near_earth_objects"][start_date]
```

Определив ресурс, можно включить его в `Definitions` вместе с ресурсом `DuckDBResource` в файле `resources.py`:

```python
# src/dagster_and_etl/defs/resources.py
@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "nasa": NASAResource(
                api_key=dg.EnvVar("NASA_API_KEY"),
            ),
            "database": DuckDBResource(
                database="data/staging/data.duckdb",
            ),
        },
    )
```

**Примечание:** для запуска пайплайна нужно задать переменную окружения `NASA_API_KEY`. Самый простой способ — создать файл `.env` в корне каталога проекта `dagster_and_etl` со следующим содержимым:

```bash
NASA_API_KEY=your_api_key_here
```

Dagster автоматически загружает файлы `.env` при запуске сервера разработки. Если сервер уже работает, перезапусти его после создания файла.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
