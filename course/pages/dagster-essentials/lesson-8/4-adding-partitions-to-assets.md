---
title: 'Урок 8: Добавление партиций к активам'
module: 'dagster_essentials'
lesson: '8'
---

# Добавление партиций к активам

В этом разделе ты обновишь активы в файле `src/dagster_essentials/defs/assets/trips.py`, чтобы использовать партиции.

Начнём с `taxi_trips_file`. Сейчас код актива должен выглядеть следующим образом:

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset
def taxi_trips_file() -> None:
    """
      The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal.
    """
    month_to_fetch = '2023-03'
    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb") as output_file:
        output_file.write(raw_trips.content)
```

В этом активе `month_to_fetch` задан как `2023-03` для получения данных за март 2023 года. С помощью `monthly_partition` можно обновить актив так, чтобы получать данные за три месяца по отдельным партициям.

Чтобы добавить партиции к активу:

1. Импортируй `monthly_partition` из модуля `partitions`, добавив следующий код в начало файла `src/dagster_essentials/defs/assets/trips.py`:

   ```python
   from dagster_essentials.defs.partitions import monthly_partition
   ```

2. В декораторе актива (`@dg.asset`) добавь параметр `partitions_def`, равный `monthly_partition`:

   ```python
   @dg.asset(
       partitions_def=monthly_partition
   )
   ```

3. В Dagster аргумент `context` предоставляет метаданные о текущей материализации. Чтобы получить к ним доступ, добавь его первым аргументом функции определения актива. Для аннотации типа укажи `dg.AssetExecutionContext` в сигнатуре функции. Например, обновлённое определение актива должно выглядеть так:

   ```python
   @dg.asset(
       partitions_def=monthly_partition
   )
   def taxi_trips_file(context: dg.AssetExecutionContext) -> None:
   ```

   **Примечание:** аргумент `context` не является специфичным для партиций. Однако в Dagster University ты используешь его впервые. Он предоставляет информацию о том, как Dagster выполняет и материализует актив. Например, можно узнать, какую партицию Dagster материализует, какое задание инициировало материализацию или какие метаданные были добавлены при предыдущих материализациях.

4. В исходном коде актива логика получения данных за март 2023 года была жёстко задана (`'2023-03'`). Используй свойство `partition_key` аргумента `context`, чтобы динамически получать данные за месяц конкретной партиции:

   ```python
   @dg.asset(
       partitions_def=monthly_partition
   )
   def taxi_trips_file(context: dg.AssetExecutionContext) -> None:
       partition_date_str = context.partition_key
   ```

5. В источнике NYC OpenData имена файлов поездок содержат даты в формате `YYYY-MM`. Однако `context.partition_key` возвращает дату материализуемой партиции в виде строки формата `YYYY-MM-DD`. Возьми срез строки, чтобы привести её к формату источника, и замени существующее объявление переменной `month_to_fetch`:

   ```python
   @dg.asset(
       partitions_def=monthly_partition
   )
   def taxi_trips_file(context: dg.AssetExecutionContext) -> None:
       partition_date_str = context.partition_key
       month_to_fetch = partition_date_str[:-3]
   ```

После выполнения этих шагов актив `taxi_trips_file` должен выглядеть примерно как следующий фрагмент:

```python
# src/dagster_essentials/defs/assets/trips.py
from dagster_essentials.defs.partitions import monthly_partition

@dg.asset(
    partitions_def=monthly_partition
)
def taxi_trips_file(context: dg.AssetExecutionContext) -> None:
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

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
