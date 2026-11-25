---
title: 'Урок 3: Материализация ассета'
module: 'dagster_essentials'
lesson: '3'
---

# Материализация ассета

Теперь, когда ассет определён в коде, следующий шаг — **материализовать** его. При материализации Dagster выполняет функцию ассета, создавая ассет и сохраняя результат в постоянном хранилище, например в хранилище данных. Начало материализации инициирует **запуск (run)**.

Чтобы лучше понять материализацию, ещё раз рассмотрим созданный ассет `taxi_trips_file` и работу его функции:

```python
# src/dagster_essentials/defs/assets/trips.py
@dg.asset
def taxi_trips_file() -> None:
    """The raw parquet files for the taxi trips dataset. Sourced from the NYC Open Data portal."""
    month_to_fetch = "2023-03"
    raw_trips = requests.get(
        f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{month_to_fetch}.parquet"
    )

    with open(
        constants.TAXI_TRIPS_TEMPLATE_FILE_PATH.format(month_to_fetch), "wb"
    ) as output_file:
        output_file.write(raw_trips.content)
```

1. Описание ассета задаётся строкой документации (docstring, `"""`), которая отображается в интерфейсе Dagster.

2. Далее определяется переменная `month_to_fetch` со значением `2023-03`, то есть март 2023 года.

3. Определяется вторая переменная `raw_trips`. Для получения файла Parquet с сайта NYC Open Data используется функция `get` библиотеки `requests` (`requests.get`).

   С учётом переменной `month_to_fetch` URL для получения файла принимает вид: `https://.../trip-data/yellow_tripdata_2023-03.parquet`

4. Далее формируется путь сохранения файла. Значение `TAXI_TRIPS_TEMPLATE_FILE_PATH` берётся из файла проекта `assets/constants.py`: `data/raw/taxi_trips_{}.parquet`

5. Файл Parquet создаётся и сохраняется по пути `data/raw/taxi_trips_2023-03.parquet`.

6. Функция ассета успешно завершает выполнение. Это сообщает Dagster, что ассет материализован, и интерфейс обновляется, отражая успешную материализацию.

Разобравшись с основами материализации, перейдём к материализации ассета `taxi_trips_file` на практике.

---

## Материализация ассетов через интерфейс Dagster

Если интерфейс Dagster больше не запущен после урока 2, выполни следующую команду в корне проекта Dagster (каталог курса `dagster_university/dagster_essentials`):

```bash
dg dev
```

Открой в браузере [`localhost:3000`](http://localhost:3000/). Страница должна выглядеть следующим образом. Если это не так, нажми **Overview** в верхней панели навигации:

![Страница Overview в интерфейсе Dagster](/images/dagster-essentials/lesson-3/overview-page.png)

Пока страница пуста, но скоро станет интереснее. Приступим к материализации ассета.

{% table %}

- Шаг 1

---

- {% width="60%" %}
  Нажми **Catalog** (или **Assets** в старых версиях) в левой боковой панели. Откроется страница, подобная показанной справа.

  **Примечание:** если страница пуста, нажми **Reload definitions**. Подробнее об этой функции поговорим в одном из следующих уроков.

  На этой странице перечислены ассеты проекта и основные сведения о них, включая:

  - Code location и Asset group (расположение кода и группа ассетов), к которым относится ассет. Мы рассмотрим их позже.
  - Статус ассета, который для `taxi_trips_file` равен **Never materialized** (никогда не материализован).

  Далее нажми ссылку **View lineage**. Откроется глобальный граф ассетов, где можно увидеть свой DAG.

- ![Обзор ассетов в интерфейсе Dagster](/images/dagster-essentials/lesson-3/assets-overview.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 2

---

- {% width="60%" %}
  Пока граф почти пуст, поскольку есть только один ассет. Но по мере добавления ассетов и зависимостей он станет интереснее.

- ![Страница глобального графа ассетов в Dagster](/images/dagster-essentials/lesson-3/global-asset-view.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 3

---

- {% width="60%" %}
  Для материализации ассета нажми кнопку **Materialize**, выделенную на изображении справа. Будет выполнена функция, определяющая создание ассета.

- ![Кнопка Materialize на странице глобального графа ассетов](/images/dagster-essentials/lesson-3/materialize-button.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 4

---

- {% width="60%" %}
  После нажатия **Materialize** внизу страницы появится фиолетовый блок, как на изображении справа. Он сообщает, что запуск успешно начался.

  **Запуск (run)** — экземпляр выполнения, материализующий один или несколько ассетов.

- ![Материализованный ассет на странице глобального графа ассетов](/images/dagster-essentials/lesson-3/materialized-asset.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 5

---

- {% width="60%" %}
  Перейди в каталог `data/raw` проекта Dagster, чтобы увидеть файл, созданный при материализации ассета: `data/raw/taxi_trips_2023-03.parquet`.

  **Примечание:** загрузка может занять некоторое время, поэтому файл появится не сразу.

- ![Файл, созданный при материализации ассета](/images/dagster-essentials/lesson-3/data-raw-parquet.png) {% rowspan=2 %}

{% /table %}

Готово! Ты успешно материализовал первый ассет! 🎉

---

## Материализация ассетов с помощью `dg`

Ассеты также можно выполнять непосредственно из командной строки с помощью `dg`. Это удобно, когда нужно выполнить ассет без запуска веб-сервера Dagster. Например:

```
dg launch --assets taxi_trips_file
```

Эта команда выполнит ассет taxi_trips_file и выведет все события запуска в терминал:

```
2025-09-17 14:19:03 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83621 - RUN_START - Started execution of run for "__ASSET_JOB".
2025-09-17 14:19:03 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83621 - ENGINE_EVENT - Executing steps using multiprocess executor: parent process (pid: 83621)
2025-09-17 14:19:03 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83621 - taxi_trips_file - STEP_WORKER_STARTING - Launching subprocess for "taxi_trips_file".
2025-09-17 14:19:04 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - taxi_trips_file - STEP_WORKER_STARTED - Executing step "taxi_trips_file" in subprocess.
2025-09-17 14:19:05 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - taxi_trips_file - RESOURCE_INIT_STARTED - Starting initialization of resources [io_manager].
2025-09-17 14:19:05 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - taxi_trips_file - RESOURCE_INIT_SUCCESS - Finished initialization of resources [io_manager].
2025-09-17 14:19:05 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - LOGS_CAPTURED - Started capturing logs in process (pid: 83628).
2025-09-17 14:19:05 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - taxi_trips_file - STEP_START - Started execution of step "taxi_trips_file".
2025-09-17 14:19:13 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - taxi_trips_file - STEP_OUTPUT - Yielded output "result" of type "Any". (Type check passed).
2025-09-17 14:19:13 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - taxi_trips_file - ASSET_MATERIALIZATION - Materialized value taxi_trips_file.
2025-09-17 14:19:13 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83628 - taxi_trips_file - STEP_SUCCESS - Finished execution of step "taxi_trips_file" in 8.9s.
2025-09-17 14:19:14 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83621 - ENGINE_EVENT - Multiprocess executor: parent process exiting after 10.68s (pid: 83621)
2025-09-17 14:19:14 -0500 - dagster - DEBUG - __ASSET_JOB - 865a6f54-7acd-4bb4-8d97-2949e149a1d5 - 83621 - RUN_SUCCESS - Finished execution of run for "__ASSET_JOB".
```

## Когда использовать `dg dev`, а когда `dg launch`

Теперь ты знаешь два способа запуска ассета. Какой выбрать? Оба подходят. Для быстрой проверки может быть удобнее выполнить ассет через `dg launch`, а по мере усложнения проекта Dagster можно использовать `dg dev`.

В большей части курса мы будем пользоваться `dg dev`, чтобы продемонстрировать больше возможностей Dagster.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
