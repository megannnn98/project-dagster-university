---
title: "Урок 6: Создание партиционированного ассета dbt"
module: 'dagster_dbt'
lesson: '6'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Создание партиционированного ассета dbt

Основа со стороны dbt готова. Теперь изменим код Dagster: зададим партиции для инкрементальных моделей и передадим dbt границы обрабатываемых данных.

Поскольку партиционировать нужно только часть моделей, создадим несколько определений `@dbt_assets`.

Сначала зададим партиции в определении `@dbt_assets`. При запуске получим временное окно активной партиции и передадим его в dbt. Затем изменим модель dbt, чтобы она выбирала записи из этого окна.

---

## Селектор инкрементальных моделей

В `defs/assets/dbt.py`:

1. Добавьте импорты:

   ```python
   from dagster_and_dbt.defs.partitions import daily_partition
   import json
   ```

   Мы импортировали `daily_partition` из `defs/partitions.py` и стандартный модуль `json`, который поможет передать границы партиции в dbt.

2. Определите константу `INCREMENTAL_SELECTOR` для выбора и исключения инкрементальных моделей:

   ```python
   INCREMENTAL_SELECTOR = "config.materialized:incremental"
   ```

   Строка использует синтаксис выбора dbt и выбирает все инкрементальные модели. В своих проектах можно ограничить выбор конкретными моделями, которые нужно партиционировать.

---

## Новая функция с @dbt_assets

Первое определение `@dbt_assets` описывало ассеты проекта dbt. Новое определение будет описывать _партиционированные_ ассеты выбранной группы моделей того же проекта.

1. В `defs/assets/dbt.py` после исходной функции определите `incremental_dbt_models`, используя тот же манифест:

   ```python
   @dbt_assets(
       manifest=dbt_project.manifest_path,
       dagster_dbt_translator=CustomizedDagsterDbtTranslator()
   )
   def incremental_dbt_models(
       context: dg.AssetExecutionContext,
       dbt: DbtCliResource
   ):
       yield from dbt.cli(["build"], context=context).stream()
   ```

2. Добавьте аргументы выбора моделей `select` и определения партиций `partitions_def`:

   ```python
   # src/dagster_and_dbt/defs/assets/dbt.py
   @dbt_assets(
       manifest=dbt_project.manifest_path,
       dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
       select=INCREMENTAL_SELECTOR,     # select only models with INCREMENTAL_SELECTOR
       partitions_def=daily_partition   # partition those models using daily_partition
   )
   def incremental_dbt_models(
       context: dg.AssetExecutionContext,
       dbt: DbtCliResource
   ):
     yield from dbt.cli(["build"], context=context).stream()
   ```

   Функция теперь выбирает только модели, соответствующие `INCREMENTAL_SELECTOR`, и задаёт им партиционирование `daily_partition`.

---

## Партиционирование incremental_dbt_models

Заполним тело функции. Через `context` можно получить сведения о запуске, в том числе временное окно партиции. Например, от `2023-03-04T00:00:00+00:00` до `2023-03-05T00:00:00+00:00`.

Перед `yield` добавьте:

```bash
time_window = context.partition_time_window
dbt_vars = {
    "min_date": time_window.start.strftime('%Y-%m-%d'),
    "max_date": time_window.end.strftime('%Y-%m-%d')
}
```

Временное окно сохраняется в `time_window`; его границы преобразуются в строки дат для dbt.

Теперь передадим их во время выполнения через `--vars`. Метод `dbt.cli` принимает те же аргументы, что и CLI dbt. Измените строку с `yield`:

```python
yield from dbt.cli(["build", "--vars", json.dumps(dbt_vars)], context=context).stream()
```

---

## Обновление dbt_analytics

У инкрементальных моделей теперь отдельное определение `@dbt_assets`, поэтому их нужно исключить из исходного определения `dbt_analytics`:

```python
# src/dagster_and_dbt/defs/assets/dbt.py
@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    exclude=INCREMENTAL_SELECTOR, # Add this here
)
def dbt_analytics(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
```

Полный файл `defs/assets/dbt.py` должен выглядеть так:

```python
import json

import dagster as dg
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets

from dagster_and_dbt.defs.partitions import daily_partition
from dagster_and_dbt.defs.project import dbt_project

INCREMENTAL_SELECTOR = "config.materialized:incremental"


class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        resource_type = dbt_resource_props["resource_type"]
        name = dbt_resource_props["name"]
        if resource_type == "source":
            return dg.AssetKey(f"taxi_{name}")
        else:
            return super().get_asset_key(dbt_resource_props)


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    exclude=INCREMENTAL_SELECTOR,
)
def dbt_analytics(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
    select=INCREMENTAL_SELECTOR,
    partitions_def=daily_partition,
)
def incremental_dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    time_window = context.partition_time_window
    dbt_vars = {
        "min_date": time_window.start.strftime('%Y-%m-%d'),
        "max_date": time_window.end.strftime('%Y-%m-%d')
    }

    yield from dbt.cli(
        ["build", "--vars", json.dumps(dbt_vars)], context=context
    ).stream()

```

---

## Обновление модели daily_metrics

Теперь передаваемые при запуске границы партиции можно прочитать в dbt через макрос `var`.

В `src/dagster_and_dbt/analytics/models/marts/daily_metrics.sql` замените условие внутри блока `{% if is_incremental() %}` следующим:

```sql
where date_of_business between '{{ var('min_date') }}' and '{{ var('max_date') }}'
```

Условие выбирает строки между `min_date` и `max_date`.

**Особенности исходного примера:** `between` включает обе границы, тогда как временные окна Dagster обычно имеют исключительную верхнюю границу. Поэтому этот фильтр может захватить начало следующей партиции. Для непересекающихся окон используйте нижнюю границу включительно и верхнюю исключительно. Кроме того, условие находится внутри `is_incremental()`: при первом создании таблицы и `full refresh` оно не применяется, и модель обрабатывает всю историю. Исходные блоки кода здесь сохранены.

---

## Запуск пайплайна

1. Перезагрузите расположение кода в Dagster. В графе появится партиционированный ассет `daily_metrics`:

   ![Ассет daily_metrics в графе Dagster](/images/dagster-dbt/lesson-6/daily-metrics-asset.png)

2. Выберите `daily_metrics` и нажмите **Materialize selected**. Сначала потребуется выбрать партиции.
3. После начала запуска откройте его страницу и изучите журнал. В оригинале курса приведён следующий пример команды:

   ```bash
   dbt build --vars {"min_date": "2023-03-04T00:00:00+00:00", "max_date": "2023-03-05T00:00:00+00:00"} --select config.materialized:incremental
   ```

   В коде выше используется `strftime('%Y-%m-%d')`, поэтому фактические значения `min_date` и `max_date` будут датами вида `2023-03-04`, а не полными временными метками из примера команды.
