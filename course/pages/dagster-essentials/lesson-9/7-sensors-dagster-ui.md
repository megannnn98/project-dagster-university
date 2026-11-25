---
title: 'Урок 9: Сенсоры в интерфейсе Dagster'
module: 'dagster_essentials'
lesson: '9'
---

# Сенсоры в интерфейсе Dagster

Теперь, когда сенсор создан, изучим интерфейс Dagster.

{% table %}

- Шаг 1

---

- {% width="60%" %}
  Перейди на страницу **Global Asset Lineage**, где должен отображаться новый актив `adhoc_request`.

  **Примечание:** если актив не виден, сначала нажми **Reload definitions**.

- ![Новый актив adhoc_request в интерфейсе Dagster](/images/dagster-essentials/lesson-9/ui-asset-lineage-with-sensors.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 2

---

- {% width="60%" %}
  Нажми **Automation**. На этой вкладке ты увидишь `adhoc_request_sensor` вместе с ранее созданными расписаниями.

  Обрати внимание, что переключатель **Running** показывает, что сенсор выключен. По умолчанию при первой загрузке сенсоры и расписания выключены.

- ![Вкладка сенсоров в интерфейсе Dagster](/images/dagster-essentials/lesson-9/ui-sensors-tab.png) {% rowspan=2 %}

{% /table %}

{% table %}

- Шаг 3

---

- {% width="60%" %}
  Нажми `adhoc_request_sensor`, чтобы открыть страницу **Sensor details**.

  Здесь можно найти подробные сведения о сенсоре, в том числе связанные задания, историю тиков и запусков и другую информацию.

- ![Страница сведений о сенсоре в интерфейсе Dagster](/images/dagster-essentials/lesson-9/ui-sensor-details.png) {% rowspan=2 %}

{% /table %}

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
