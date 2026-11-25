---
title: 'Дополнительный раздел: Метаданные материализации'
module: 'dagster_essentials'
lesson: 'extra-credit'
---

# Метаданные материализации

Теперь, когда мы рассмотрели метаданные определения, перейдём к другому типу — метаданным материализации.

---

## Добавление метаданных материализации к активу

Чтобы добавить метаданные к активу, нужно сделать две вещи:

- Вернуть из актива объект `MaterializeResult` с параметром `metadata`.
- Обернуть данные с помощью вспомогательного класса `MetadataValue`, чтобы они корректно отображались в интерфейсе.

Для наглядности добавим метаданные к активу `taxi_trips_file`. Это позволит записывать количество записей в метаданные материализации актива.

1. Открой файл `assets/trips.py`.

2. Найди актив `taxi_trips_file`. На данном этапе курса он должен выглядеть следующим образом:

   ```python
   # src/dagster_essentials/defs/assets/trips.py
   import dagster as dg
   import requests
   from dagster_essentials.defs.assets import constants
   from dagster_essentials.defs.partitions import monthly_partition

   @dg.asset(
       partitions_def=monthly_partition,
       group_name="raw_files",
   )
   def taxi_trips_file(context) -> None:
       """
         The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
       """

       partition_date_str = context.partition_key
       month_to_fetch = partition_date_str[:-3]

       raw_trips = requests.get(
           f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
       )

       with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
           output_file.write(raw_trips.content)
   ```

3. Сначала нужно вычислить количество записей в файле. Скопируй следующий код после последней строки актива:

   ```python
   num_rows = len(pd.read_parquet(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)))
   ```

4. Далее добавим метаданные с указанным типом:

   ```python
   return dg.MaterializeResult(
       metadata={
           'Number of records': dg.MetadataValue.int(num_rows)
       }
   )
   ```

5. Поскольку теперь функция возвращает значение, обновим тип возвращаемого значения актива на `MaterializeResult`:

   ```python
   import dagster as dg

   @dg.asset(
       partitions_def=monthly_partition,
       group_name="raw_files",
   )
   def taxi_trips_file(context) -> dg.MaterializeResult:
   ```

   Разберём, что происходит:

   - Вместо того чтобы ничего не возвращать, мы вернём информацию о произошедшей материализации с помощью класса `MaterializeResult`.
   - Параметр `metadata` принимает словарь `dict`, где ключ — метка или имя метаданных, а значение — сами данные. В данном случае ключом является `Number of records`. Значение — выражение после `Number of records`.
   - С помощью `MetadataValue.int` значение переменной `num_rows` обозначается как целое число. Это сообщает Dagster, что данные нужно отображать как целое число.

   На этом этапе актив должен выглядеть так:

   ```python
   # src/dagster_essentials/defs/assets/trips.py
   import pandas as pd
   import dagster as dg

   @dg.asset(
       partitions_def=monthly_partition,
       group_name="raw_files",
   )
   def taxi_trips_file(context) -> dg.MaterializeResult:
       """
         The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
       """

       partition_date_str = context.partition_key
       month_to_fetch = partition_date_str[:-3]

       raw_trips = requests.get(
           f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
       )

       with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
           output_file.write(raw_trips.content)

       num_rows = len(pd.read_parquet(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch)))

       return dg.MaterializeResult(
           metadata={
               'Number of records': dg.MetadataValue.int(num_rows)
           }
       )
   ```

---

## Метаданные материализации в интерфейсе Dagster

Теперь посмотрим на метаданные в интерфейсе Dagster. Это удобный способ изучить данные и убедиться, что всё сохранилось как ожидалось.

1. Перейди на страницу **Global Asset Lineage**.
2. Нажми **Reload definitions**.
3. Когда определения загрузятся, выбери актив `taxi_trips_file` и материализуй все его партиции.

После завершения материализации актива можно будет просмотреть связанные с ним графики. На оси X отмечены партиции с подписями месяцев, а на оси Y — количество записей в каждой партиции.

Эти метаданные также можно просмотреть, нажав **View in Asset Catalog** под именем актива и затем перейдя на вкладку **Plots**.

![График метаданных актива taxi_trips_file на вкладке Asset Catalog > Plots](/images/dagster-essentials/extra-credit/ui-plots-tab.png)

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
