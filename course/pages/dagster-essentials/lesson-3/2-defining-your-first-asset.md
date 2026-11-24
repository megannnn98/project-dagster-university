---
title: 'Урок 3: Определение первого актива'
module: 'dagster_essentials'
lesson: '3'
---

# Определение первого актива

В этом курсе ты будешь использовать данные [NYC OpenData](https://opendata.cityofnewyork.us/) для анализа поездок на такси в Нью-Йорке. Первый актив использует данные [TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), содержащие записи о поездках нескольких типов транспортных средств. В этом активе мы сосредоточимся на данных о поездках жёлтых такси.

Первый актив, который ты назовёшь `taxi_trips_file`, получит данные о поездках жёлтых такси за март 2023 года и сохранит их на локальном компьютере.

## Структура проекта

Прежде чем писать первый актив, поговорим о структуре проектов Dagster. В предыдущем уроке мы упомянули `dg` и его полезные возможности для быстрого начала работы. Например, команда `dg scaffold project` может подготовить виртуальное окружение `uv`, но мы уже настроили его при подготовке курса в уроке 2.

Теперь с помощью `dg` можно сгенерировать файл первого актива. Выполни следующую команду:

**Примечание:** команды `dg` нужно запускать внутри проекта Dagster, относящегося к курсу (в данном случае `dagster_university/dagster_essentials`). При этом команда `dg` может выполняться из любого каталога внутри проекта.

```bash
dg scaffold defs dagster.asset assets/trips.py
```

В проекте Dagster появится файл `trips.py`.

```
.
└── src
    └── dagster_essentials
        └── defs
            └── assets
                ├── __init__.py
                ├── constants.py # already present
                └── trips.py
```

**Примечание:** если бы мы создавали проект Dagster с нуля, то использовали бы [`uvx create-dagster`](https://docs.dagster.io/getting-started/installation), который создаёт полноценный проект Dagster и виртуальное окружение. Но мы работаем в уже инициализированном репозитории, поэтому можем пропустить этот шаг.

Использование `dg` для генерации каркаса проекта гарантирует размещение файлов в правильных каталогах. С помощью `dg` также можно проверить корректность конфигурации.

```bash
> dg check defs
All component YAML validated successfully.
All definitions loaded successfully.
```

Это ожидаемый результат: хотя мы создали файл будущего актива, код актива в нём ещё отсутствует.

## Определение первого актива

Теперь, когда файлы подготовлены, можно добавить первый актив.

1. Открой созданный файл `src/dagster_essentials/defs/assets/trips.py` в проекте Dagster. Здесь ты будешь писать код актива.

2. Удали из `trips.py` автоматически сгенерированный код и замени его следующими импортами:

   ```python
   import requests
   from dagster_essentials.defs.assets import constants
   ```

3. Ниже импортов определим функцию без входных параметров, которая ничего не возвращает (аннотация типа `None`). Добавь следующий код функции с именем `taxi_trips_file`:

   ```python
   # src/dagster_essentials/defs/assets/trips.py
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

4. Чтобы превратить функцию в актив Dagster, нужно сделать две вещи:

   1. Импортировать библиотеку Dagster:

      ```python
      import dagster as dg
      ```

   2. Добавить декоратор `@dg.asset` перед функцией `taxi_trips_file`. Теперь код должен выглядеть следующим образом:

      ```python
      # src/dagster_essentials/defs/assets/trips.py
      import requests
      from dagster_essentials.defs.assets import constants
      import dagster as dg

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

Готово: ты создал первый актив Dagster! С помощью декоратора `@dg.asset` можно превратить существующую функцию Python в актив Dagster.

Снова воспользуемся `dg`, чтобы проверить актив:

```bash
> dg check defs
All component YAML validated successfully.
All definitions loaded successfully.
```

**Возникли вопросы о записи `-> None`?** Это возможность Python, называемая **аннотацией типа**. В данном случае она указывает, что функция ничего не возвращает. Подробнее об аннотациях типов можно узнать в [документации Python](https://docs.python.org/3/library/typing.html). Мы настоятельно рекомендуем использовать аннотации типов, чтобы код было легче читать и понимать.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
