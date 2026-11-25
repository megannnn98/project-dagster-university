---
title: 'Урок 3: Устранение ошибок запуска'
module: 'dagster_essentials'
lesson: '3'
---

# Устранение ошибок запуска

Теперь, когда ты знаешь, как материализуются ассеты и где искать сведения об их выполнении, сосредоточимся на устранении неполадок. Для демонстрации намеренно вызовем ошибку в ассете `taxi_trips_file`.

В файле `assets/trips.py` закомментируй строку `from dagster_essentials.defs.assets import constants`, чтобы код выглядел следующим образом:

```python
# src/dagster_essentials/defs/assets/trips.py
import requests
# from dagster_essentials.defs.assets import constants # <---- Import commented out here
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

В интерфейсе Dagster перейди на страницу **Global asset lineage** и снова нажми Materialize, чтобы попытаться материализовать ассет `taxi_trips_file`. Как и ожидалось, запуск завершится ошибкой, а ассет в графе будет выглядеть так:

![Ассет taxi_trips_file с ошибкой](/images/dagster-essentials/lesson-3/failed-asset.png)

Нажми на **дату** в ассете, чтобы снова открыть страницу **Run details**. Как видишь, она заметно отличается от зелёного успешного запуска, который мы наблюдали раньше:

![Страница Run details с неудачным запуском](/images/dagster-essentials/lesson-3/failed-run-details-page.png)

Когда запуск завершается ошибкой, страница Run details указывает на проблему следующим образом:

- Отображает статус **Failure** в разделе **Run stats**.
- Выделяет проблемный шаг или шаги красным цветом на **Run timeline**.
- Перечисляет проблемные шаги в разделе **Errored** рядом с **Run timeline**.
- Показывает подробные сведения об ошибках проблемных шагов в **Run logs**.

Чтобы выяснить причину сбоя, подробнее рассмотрим журналы. В этом примере воспользуемся **структурированным представлением** журналов.

---

## Использование журналов для устранения неполадок

{% table %}

- Шаг 1

---

- {% width="60%" %}
  Найди в журналах неудавшийся шаг по событию STEP_FAILURE. Проблемный шаг выделен на изображении справа.

- ![Выделенное событие STEP_FAILURE в журналах запуска](/images/dagster-essentials/lesson-3/run-failure-step.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 2

---

- {% width="60%" %}
  В столбце **INFO** неудавшегося шага нажми кнопку View full message, чтобы увидеть полную трассировку стека. Откроется всплывающее окно, подобное показанному справа.

  Теперь можно использовать трассировку стека для определения и устранения причины ошибки. В данном случае мы не импортировали `constants`, поэтому это имя не определено.

  Для исправления раскомментируй строку `from dagster_essentials.defs.assets import constants` в файле `trips.py` и сохрани файл.

  В интерфейсе Dagster нажми **Done**, чтобы закрыть всплывающее окно журналов запуска.

- ![Полная трассировка стека ошибки после нажатия View full message](/images/dagster-essentials/lesson-3/stacktrace-error.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 3

---

- {% width="60%" %}
  После восстановления импорта и сохранения файла `trips.py` выполни запуск повторно.

  На странице Run details найди и нажми кнопку **Re-execute all (\*)** в правом верхнем углу. Это приведёт к повторному выполнению всех шагов запуска.

- ![Выделенная кнопка Re-execute all на странице Run details](/images/dagster-essentials/lesson-3/highlighted-re-execute.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 4

---

- {% width="60%" %}
  Теперь запуск должен успешно материализовать ассет!

  Страница Run details будет выглядеть примерно как на изображении справа: первоначальный запуск (root run) завершился ошибкой, но повторное выполнение было успешным.

- ![Страница Run details после успешного повторного выполнения](/images/dagster-essentials/lesson-3/re-execute-successful.png) {% rowspan=2 %}

{% /table %}

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
