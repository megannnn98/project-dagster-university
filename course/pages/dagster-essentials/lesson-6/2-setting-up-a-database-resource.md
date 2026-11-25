---
title: 'Урок 6: Настройка ресурса базы данных'
module: 'dagster_essentials'
lesson: '6'
---

# Настройка ресурса базы данных

На протяжении курса ты использовал DuckDB для хранения и преобразования данных. Каждый раз, когда DuckDB использовалась в ассете, требовалось установить подключение к ней. Например:

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset(
    deps=["taxi_trips_file"],
)
def taxi_trips() -> None:
    ...
    conn = backoff(
        fn=duckdb.connect,
        retry_on=(RuntimeError, duckdb.IOException),
        kwargs={
            "database": os.getenv("DUCKDB_DATABASE"),
        },
        max_retries=10,
    )
    ...
```

Каждый ассет, выполняющий запросы к DuckDB, содержит строку `duckdb.connect`. Как уже отмечалось, с ростом проекта такой код становится хрупким и подверженным ошибкам: увеличивается число использующих его ассетов или сложность подключений, например к MotherDuck, определённому бакету S3, либо возникает необходимость загрузить расширение. В частности, проблема затрагивает следующие ассеты:

- `taxi_zones`
- `taxi_trips`
- `manhattan_stats`
- `trips_by_week`

Воспользуемся ресурсом Dagster для управления этим подключением и его совместного использования всеми соответствующими ассетами.

---

## Определение ресурса

С помощью `dg` можно создать каркас ресурса примерно так же, как мы создавали каркасы ассетов в уроке 3.

```bash
dg scaffold defs dagster.resources resources.py
```

Эта команда добавляет файл `resources.py` внутри модуля `dagster_essentials`.

```
.
└── src
    └── dagster_essentials
        └── defs
            └── resources.py
```

В только что созданный файл добавь следующий код:

```python
# src/dagster_essentials/defs/resources.py
from dagster_duckdb import DuckDBResource


database_resource = DuckDBResource(
    database="data/staging/data.duckdb"
)
```

Этот фрагмент кода импортирует ресурс `DuckDBResource` из библиотеки интеграции Dagster `dagster_duckdb`. Затем создаётся экземпляр этого ресурса и сохраняется в переменной `database_resource`.

---

## Использование переменных окружения

При работе в разных окружениях или с конфиденциальными значениями, такими как пароли, переменные окружения представляют собой стандартный способ хранения конфигурации и учётных данных. Переменные окружения не являются особенностью Python: это значения, хранящиеся вне программного обеспечения и используемые внутри него. Для знакомства с переменными окружения в Python прочитай [эту статью в нашем блоге](https://dagster.io/blog/python-environment-variables).

При настройке ресурсов рекомендуется загружать конфигурацию и секреты в программы из переменных окружения. Ты уже следовал этому подходу, используя `os.getenv` для получения переменных окружения из файла `.env`, входящего в состав проекта. Файл `.env` — распространённый способ определения переменных окружения на уровне проекта. Его **не следует** добавлять в git, поскольку такие файлы часто содержат пароли и конфиденциальную информацию.

Однако в этом проекте файл `.env` содержит только одну переменную окружения: `DUCKDB_DATABASE`. В ней задан путь к файлу базы данных DuckDB — `data/staging/data.duckdb`. Упростим код с помощью вспомогательного класса Dagster `EnvVar`.

В файле `resources.py` замени значение параметра `database` на `EnvVar`, как показано ниже:

```python
# src/dagster_essentials/defs/resources.py
from dagster_duckdb import DuckDBResource
import dagster as dg

database_resource = DuckDBResource(
    database=dg.EnvVar("DUCKDB_DATABASE")      # replaced with environment variable
)
```

`EnvVar` похож на метод `os.getenv`, который ты использовал ранее, но есть важное различие при конфигурировании ресурса:

- `EnvVar` получает значение переменной окружения **при запуске выполнения**.
- `os.getenv`, вызванный в определении ресурса, получает значение переменной окружения **при загрузке расположения кода**.

Используя `EnvVar` вместо `os.getenv`, можно динамически изменять конфигурацию ресурса. Например, изменить используемую базу DuckDB без перезапуска веб-сервера Dagster, если новое значение доступно окружению процесса выполнения.

---

## Обновление объекта Definitions

В предыдущем уроке ты узнал, что такое расположения кода, как они работают и как объединять ассеты и другие определения Dagster с помощью объекта `Definitions`.

Ты видел, что при создании каркаса проекта с помощью `dg` объект `Definitions` автоматически загружает ассеты внутри модуля. То же самое справедливо для ресурсов, однако в файл `resources.py` необходимо внести ещё одно изменение.

1. Добавь в файл `resources.py` следующий код:

   ```python
   # src/dagster_essentials/defs/resources.py
   ...

   @dg.definitions
   def resources() -> dg.Definitions:
       return dg.Definitions(resources={"database": database_resource})
   ```

   Это сообщает Dagster, как сопоставлять ресурсы с конкретными именами ключей. В данном случае только что определённый ресурс `database_resource` сопоставляется с ключом `database`.

   Теперь файл `resources.py` должен выглядеть так:

   ```python
   # src/dagster_essentials/defs/resources.py
   from dagster_duckdb import DuckDBResource
   import dagster as dg

   database_resource = DuckDBResource(
       database=dg.EnvVar("DUCKDB_DATABASE")
   )

   @dg.definitions
   def resources() -> dg.Definitions:
       return dg.Definitions(resources={"database": database_resource})
   ```

2. В интерфейсе Dagster нажми **Deployment**.

3. На вкладке **Code locations** нажми кнопку **Reload** рядом с расположением кода `dagster_essentials`.

4. Нажми на расположение кода, чтобы открыть его.

5. На открывшейся странице расположения кода перейди на вкладку **Definitions**.

6. Нажми **Resources** на левой боковой панели и выбери ресурс с именем **database**.

   Обрати внимание, что вкладка **Uses** вверху пока показывает **0**. Ресурс уже определён и загружен, но ни один из ассетов в расположении кода пока его не использует.

Теперь, когда ресурс настроен, пора использовать его в проекте. В следующем разделе ты узнаешь, как отрефакторить ассеты для работы с ресурсами.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
