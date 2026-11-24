---
title: 'Урок 4: Загрузка данных в базу данных'
module: 'dagster_essentials'
lesson: '4'
---

# Загрузка данных в базу данных

Теперь, когда у тебя есть запрос, создающий актив, воспользуемся Dagster для управления его материализацией. Когда Dagster управляет определением и материализацией активов данных, легко определить, когда изменяется таблица и сколько времени занимает её обновление.

1. В начале файла `trips.py` импортируй `duckdb` и `os` для управления расположением файла базы DuckDB, а также `backoff` из `dagster._utils`, который поможет эффективнее работать с DuckDB:

   ```python
   import duckdb
   import os
   import dagster as dg
   from dagster._utils.backoff import backoff
   ```

2. Скопируй приведённый ниже код в конец файла `trips.py`. Обрати внимание, насколько он похож на код определения активов `taxi_trips_file` и `taxi_zones`:

   ```python
   # src/dagster_essentials/defs/assets/trips.py
   @dg.asset(
       deps=["taxi_trips_file"]
   )
   def taxi_trips() -> None:
       """
         The raw taxi trips dataset, loaded into a DuckDB database
       """
       query = """
           create or replace table trips as (
             select
               VendorID as vendor_id,
               PULocationID as pickup_zone_id,
               DOLocationID as dropoff_zone_id,
               RatecodeID as rate_code_id,
               payment_type as payment_type,
               tpep_dropoff_datetime as dropoff_datetime,
               tpep_pickup_datetime as pickup_datetime,
               trip_distance as trip_distance,
               passenger_count as passenger_count,
               total_amount as total_amount
             from 'data/raw/taxi_trips_2023-03.parquet'
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

   Разберём, что делает этот код:

   1. С помощью декоратора `@dg.asset` создаётся актив с именем `taxi_trips`.

   2. Через аргумент `deps` актив `taxi_trips_file` определяется как зависимость актива `taxi_trips`.

   3. Создаётся переменная `query`, содержащая SQL-запрос. Он создаёт таблицу `trips` на основе данных файла `data/raw/taxi_trips_2023-03.parquet`, который создаётся активом `taxi_trips_file`.

   4. Создаётся переменная `conn`, представляющая подключение к базе DuckDB в проекте. Для этого сначала используется вспомогательная функция Dagster `backoff`. Она позволяет повторять попытки подключения, если ресурс DuckDB временно заблокирован другим активом. Функция принимает вызываемую функцию (в данном случае метод `.connect` библиотеки `duckdb`), типы ошибок, при которых нужно повторить попытку (`RuntimeError` и `duckdb.IOException`), максимальное число повторных попыток и аргументы метода `.connect`. Здесь передаётся переменная окружения `DUCKDB_DATABASE`, указывающая DuckDB расположение базы данных.

      Переменная окружения `DUCKDB_DATABASE` из файла `.env` проекта имеет значение `data/staging/data.duckdb`. **Примечание:** этот файл был настроен в уроке 2. При необходимости вернись к нему. Если файл настроен неправильно, материализация завершится ошибкой.

   5. Наконец, вызывается метод DuckDB `execute` объекта `conn`, которому передаётся SQL-запрос (`query`). Таким образом, при материализации актив подключается к базе DuckDB и выполняет запрос из переменной `query`.

3. Сохрани изменения в файле.

4. В интерфейсе Dagster перейди на страницу **Global asset lineage**:

   ![Граф активов taxi_trips_file и taxi_zones_file в интерфейсе Dagster](/images/dagster-essentials/lesson-4/asset-graph.png)

   Похоже, возникла проблема: новый актив `taxi_trips` не отображается. Дело в том, что необходимо перезагрузить определения в твоём **расположении кода (code location)**, чтобы новый актив появился.

   Подробнее о расположениях кода поговорим в одном из следующих уроков, а пока можно вручную перезагрузить определения, нажав кнопку **Reload Definitions** в правом верхнем углу страницы.

После перезагрузки актив `taxi_trips` появится на графе активов:

![Актив taxi_trips на графе активов в интерфейсе Dagster](/images/dagster-essentials/lesson-4/taxi-trips-in-asset-graph.png)

Обрати внимание на стрелку от файлового актива `taxi_trips_file` к активу `taxi_trips`: она обозначает зависимость `taxi_trips` от `taxi_trips_file`.

{% callout %}

> 💡 **Когда нужно перезагружать определения?** Если ты установил зависимости командой `pip install -e ".[dev]"`, перезагрузка определений потребуется только при добавлении новых активов или других объектов Dagster, например расписаний. Благодаря флагу редактируемой установки `-e` Dagster может подхватывать изменения кода функций активов без повторной перезагрузки расположения кода.
> {% /callout %}

---

## Материализация пайплайна

Нажми **Materialize all** в правом верхнем углу графа, чтобы создать запуск, материализующий все активы. Когда запуск начнётся, нажми ссылку на него в активе, чтобы открыть страницу **Run details**. Здесь можно наблюдать за выполнением запуска.

На этой странице будут видны все три материализуемых актива. Активы `taxi_trips_file` и `taxi_zones_file` должны материализоваться параллельно, а материализация `taxi_trips` начнётся только после завершения материализации `taxi_trips_file`:

![Временная шкала материализации taxi_trips_file, taxi_zones_file и taxi_trips: первые два актива выполняются параллельно, а taxi_trips ожидает успешной материализации taxi_trips_file](/images/dagster-essentials/lesson-4/materialization-graph.png)

Это происходит потому, что с помощью аргумента deps= ты указал Dagster, что taxi_trips зависит от taxi_trips_file. В этом запуске актив taxi_trips ожидает успешной материализации taxi_trips_file, прежде чем начать собственную материализацию.

### Дополнительно: проверка материализации

Чтобы убедиться в успешной материализации актива `taxi_trips`, можно обратиться к созданной таблице `trips` в DuckDB. В новом сеансе терминала открой интерактивный интерпретатор Python и выполни следующий код:

```python
import duckdb
conn = duckdb.connect(database="data/staging/data.duckdb") # assumes you're writing to the same destination as specified in .env.example
conn.execute("select count(*) from trips").fetchall()
```

Команда должна успешно выполниться и вернуть количество строк загруженных данных о поездках на такси. Закончив проверку, обязательно останови процесс в терминале перед продолжением, иначе может возникнуть ошибка. Для остановки используй `Control+C` или `Command+C`.

Поздравляем! Ты написал простой пайплайн данных, который получает данные из внешнего источника и загружает их в базу данных.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
