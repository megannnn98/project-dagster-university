---
title: "Урок 5: Автоматизация моделей dbt в Dagster"
module: 'dagster_dbt'
lesson: '5'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Автоматизация моделей dbt в Dagster

Модели dbt уже включены в регулярное выполнение благодаря существующему расписанию проекта Dagster.

Откройте **Jobs** в интерфейсе Dagster и выберите `trip_update_job`. Среди ассетов задания уже есть модели dbt:

![Ассеты dbt в задании trip_update_job](/images/dagster-dbt/lesson-5/trip-update-job-dbt-assets.png)

Откройте `defs/jobs.py` и рассмотрите определение `trip_update_job`:

```python
# src/dagster_and_dbt/defs/jobs.py
trip_update_job = dg.define_asset_job(
    name="trip_update_job",
    partitions_def=monthly_partition,
    selection=dg.AssetSelection.all() - trips_by_week - adhoc_request
)
```

Модели включены в задание благодаря `AssetSelection.all()`. После загрузки проекта dbt в Dagster его модели становятся ассетами и участвуют в обычном выборе ассетов.

---

## Исключение отдельных моделей dbt

Интеграция Dagster учитывает привычные способы работы с dbt и предоставляет вспомогательные функции с его синтаксисом выбора моделей. Используем одну из них для явного исключения моделей из задания.

Предположим, вы вместе с аналитическим инженером дорабатываете `stg_trips` и планируете добавить зависимые модели. Пока пайплайн нестабилен, нужно исключить `stg_trips` и все нижестоящие модели dbt из регулярного задания. Ваш коллега хорошо знает dbt, но пока мало знаком с Dagster.

Функция [`build_dbt_asset_selection`](https://docs.dagster.io/_apidocs/libraries/dagster-dbt#dagster_dbt.build_dbt_asset_selection) позволяет использовать привычный синтаксис dbt. Она принимает:

- Список определений `@dbt_assets`, из которых выбираются модели.
- Строку выбора моделей в [синтаксисе dbt](https://docs.getdbt.com/reference/node-selection/syntax).

Функция возвращает `AssetSelection` для подходящих моделей dbt.

1. В начало `defs/jobs.py` добавьте импорты `dbt_analytics` из `assets.dbt` и `build_dbt_asset_selection` из `dagster_dbt`:

    ```python
    from dagster_and_dbt.defs.assets.dbt import dbt_analytics
    from dagster_dbt import build_dbt_asset_selection
    ```

2. После остальных выражений выбора определите `dbt_trips_selection`. Передайте `dbt_analytics` и строку, выбирающую `stg_trips` со всеми нижестоящими моделями dbt:

    ```python
    dbt_trips_selection = build_dbt_asset_selection([dbt_analytics], "stg_trips+")
    ```

3. Вычтите `dbt_trips_selection` из аргумента `selection` задания `trip_update_job`:

    ```python
    trip_update_job = dg.define_asset_job(
        name="trip_update_job",
        partitions_def=monthly_partition,
        selection=dg.AssetSelection.all() - trips_by_week - adhoc_request - dbt_trips_selection
    )
    ```

4. Перезагрузите расположение кода и убедитесь, что выбранные модели dbt больше не входят в `trip_update_job`:

   ![Задание trip_update_job после исключения моделей dbt](/images/dagster-dbt/lesson-5/job-with-dbt-models.png)

Ассет `airport_trips` по-прежнему включён в задание: `build_dbt_asset_selection` выбирает только _модели dbt_, не охватывая написанные вами ассеты Dagster.

Чтобы исключить также `airport_trips` и другие нижестоящие ассеты, используйте метод Dagster `.downstream()`. Теперь `+` в селекторе dbt не нужен:

```python
dbt_trips_selection = build_dbt_asset_selection([dbt_analytics], "stg_trips").downstream()
```

Перезагрузите расположение кода и ещё раз проверьте состав `trip_update_job`.

{% callout %}
> 💡 Для быстрого создания задания и расписания на основе выбора моделей dbt можно использовать похожую функцию [`build_schedule_from_dbt_selection`](https://docs.dagster.io/_apidocs/libraries/dagster-dbt#dagster_dbt.build_schedule_from_dbt_selection).
{% /callout %}
