---
title: 'Урок 9: Включение сенсора'
module: 'dagster_essentials'
lesson: '9'
---

# Включение сенсора

Поскольку сенсоры по умолчанию выключены, для использования сенсора его необходимо включить. В этом разделе рассмотрим работу с сенсором в интерфейсе Dagster.

{% table %}

- Шаг 1

---

- {% width="60%" %}
  В каталоге `data/requests` находится файл `README` с инструкциями по запуску сенсора. Используй пример `.json` из README, чтобы создать новый файл `january-staten-island.json` с кодом справа.

- {% rowspan=2 %}
  ```json
  {
    "start_date": "2023-01-10",
    "end_date": "2023-01-25",
    "borough": "Staten Island"
  }
  ```

{% /table %}

{% table %}

- Шаг 2

---

- {% width="60%" %}
  Dagster позволяет проверять сенсоры непосредственно через интерфейс. Это удобно для моделирования ситуаций, когда сенсоры срабатывают слишком часто или недостаточно часто.

  1. Если ты ушёл со страницы **Sensor details** сенсора `adhoc_request_sensor`, вернись на неё.

  2. На этой странице нажми **Preview tick result** в правом верхнем углу. Это позволяет выполнить один тик без включения сенсора.

  3. Нажми **Continue**, затем **Apply requests & commit tick result**, чтобы начать проверку.

- ![Диалог проверки сенсора в интерфейсе Dagster](/images/dagster-essentials/lesson-9/ui-test-sensor-dialog.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 3

---

- {% width="60%" %}
  После завершения проверки отобразятся результаты. Нажми **Open in Launchpad**, чтобы перейти к заданию `adhoc_request_job`.

{% /table %}

{% table %}

- Шаг 4

---

- {% width="60%" %}
  Обрати внимание, что в Launchpad уже подставлена конфигурация из файла `january-staten-island.json`.

  Нажми **Launch Run** внизу страницы, чтобы отправить запрос на запуск.

- ![Launchpad задания adhoc_request_job с конфигурацией из файла january-staten-island.json](/images/dagster-essentials/lesson-9/ui-launchpad.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 5

---

- {% width="60%" %}
  После завершения запуска перейди в каталог `data/outputs` проекта, куда актив сохранил выходной файл. Ты должен увидеть столбчатую диаграмму, подобную показанной справа.

- ![Столбчатая диаграмма количества поездок по часам суток на Статен-Айленде в январе 2023 года](/images/dagster-essentials/lesson-9/trips-graph.png) {% rowspan=2 %}

{% /table %}

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
