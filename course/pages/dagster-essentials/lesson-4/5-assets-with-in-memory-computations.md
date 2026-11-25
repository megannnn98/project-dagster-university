---
title: 'Урок 4: Ассеты с вычислениями в оперативной памяти'
module: 'dagster_essentials'
lesson: '4'
---

# Ассеты с вычислениями в оперативной памяти

До сих пор при написании ассетов ты управлял вычислениями в базе данных и выполнял простые операции в Python, например скачивание файла. В этом разделе ты научишься с помощью Dagster управлять вычислениями на Python: генерировать и преобразовывать данные и строить отчёт.

### Создание метрик с помощью ассетов

Управлять всеми ассетами в одном файле становится сложно. Разделим ассеты по назначению и поместим ассеты, предназначенные для анализа, в отдельный файл, отдельно от ассетов загрузки данных.

1. С помощью `dg` создай новый файл для ассетов, вычисляющих метрики:

    ```bash
    dg scaffold defs dagster.asset assets/metrics.py
    ```

2. В начале файла `src/dagster_essentials/defs/assets/metrics.py` добавь следующие импорты:

   ```python
   import dagster as dg

   import matplotlib.pyplot as plt
   import geopandas as gpd

   import duckdb
   import os

   from dagster_essentials.defs.assets import constants
   ```

   Некоторые импорты могут быть тебе незнакомы, но мы рассмотрим их по мере использования.

3. Далее определи ассет `manhattan_stats` и его зависимости. Скопируй следующий код в конец файла `metrics.py`:

   ```python
   @dg.asset(
       deps=["taxi_trips", "taxi_zones"]
   )
   def manhattan_stats() -> None:
   ```

4. Теперь добавим логику вычисления `manhattan_stats`. Обнови определение ассета `manhattan_stats` следующим образом:

   ```python
   # src/dagster_essentials/defs/assets/metrics.py
   @dg.asset(
       deps=["taxi_trips", "taxi_zones"]
   )
   def manhattan_stats() -> None:
       query = """
           select
               zones.zone,
               zones.borough,
               zones.geometry,
               count(1) as num_trips,
           from trips
           left join zones on trips.pickup_zone_id = zones.zone_id
           where borough = 'Manhattan' and geometry is not null
           group by zone, borough, geometry
       """

       conn = duckdb.connect(os.getenv("DUCKDB_DATABASE"))
       trips_by_zone = conn.execute(query).fetch_df()

       trips_by_zone["geometry"] = gpd.GeoSeries.from_wkt(trips_by_zone["geometry"])
       trips_by_zone = gpd.GeoDataFrame(trips_by_zone)

       with open(constants.MANHATTAN_STATS_FILE_PATH, 'w') as output_file:
           output_file.write(trips_by_zone.to_json())
   ```

   Разберём код. Он:

   1. Формирует SQL-запрос, объединяющий таблицы `trips` и `zones`, оставляющий только поездки на Манхэттене и агрегирующий данные для вычисления количества поездок по каждому району.
   2. Выполняет запрос к той же базе DuckDB, в которую были загружены данные в других ассетах.
   3. Использует библиотеку [GeoPandas](https://geopandas.org/en/stable/) для преобразования координат в формат, пригодный для других библиотек.
   4. Сохраняет преобразованные данные в файл GeoJSON.

---

## Материализация метрик

Перезагрузи определения в интерфейсе. Ассет `manhattan_stats` должен появиться на графе ассетов. Выбери его и нажми **Materialize selected**.

После успешного завершения материализации убедись, что по пути `data/staging/manhattan_stats.geojson` находится большой, но корректный JSON-файл.

---

## Создание карты

В этом разделе ты создашь ассет, зависящий от `manhattan_stats`, загружающий его данные GeoJSON и создающий на их основе визуализацию.

1. Скопируй следующий код в конец файла `metrics.py`:

   ```python
   # src/dagster_essentials/defs/assets/metrics.py
   @dg.asset(
       deps=["manhattan_stats"],
   )
   def manhattan_map() -> None:
       trips_by_zone = gpd.read_file(constants.MANHATTAN_STATS_FILE_PATH)

       fig, ax = plt.subplots(figsize=(10, 10))
       trips_by_zone.plot(column="num_trips", cmap="plasma", legend=True, ax=ax, edgecolor="black")
       ax.set_title("Number of Trips per Taxi Zone in Manhattan")

       ax.set_xlim(-74.05, -73.90)  # Adjust longitude range
       ax.set_ylim(40.70, 40.82)  # Adjust latitude range
       
       # Save the image
       plt.savefig(constants.MANHATTAN_MAP_FILE_PATH, format="png", bbox_inches="tight")
       plt.close(fig)
   ```

   Приведённый код выполняет следующие действия:

   1. Определяет новый ассет `manhattan_map`, зависящий от `manhattan_stats`.
   2. Загружает файл GeoJSON обратно в оперативную память.
   3. Создаёт карту для визуализации данных с помощью библиотеки [Matplotlib](https://matplotlib.org/).
   4. Сохраняет визуализацию в формате PNG.

2. В интерфейсе нажми **Reload Definitions**, чтобы Dagster обнаружил новый ассет.

3. На графе ассетов выбери `manhattan_map` и нажми **Materialize selected**.

4. Открой файл `data/outputs/manhattan_map.png`, чтобы убедиться в успешной материализации. Файл должен выглядеть следующим образом:

   ![Материализованная карта Манхэттена с количеством поездок по зонам такси](/images/dagster-essentials/lesson-4/materialized-map.png)

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
