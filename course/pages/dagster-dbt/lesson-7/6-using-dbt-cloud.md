---
title: "Урок 7: Использование dbt Cloud"
module: 'dbt_dagster'
lesson: '7'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Использование dbt Cloud

До сих пор мы выполняли команды dbt локально и в CI/CD через CLI и `DbtCliResource`. Если ваша команда использует dbt Cloud, Dagster подключается к нему через API и выполняет команды удалённо.

Рассмотрим отличия и общие принципы.

---

## Отличия интеграции с dbt Cloud

| | CLI dbt в этом курсе | dbt Cloud |
|---|---|---|
| Декоратор | `@dbt_assets` | `@dbt_cloud_assets` |
| Ресурс | `DbtCliResource` | `DbtCloudWorkspace` |
| Источник манифеста | Локальная генерация через `dbt parse` | Получение через API dbt Cloud |
| Объект проекта | `DbtProject` | Не используется |
| `prepare_if_dev()` | Используется при локальной разработке | Не применяется |
| Тело функции | `yield from dbt.cli([...]).stream()` | `yield from dbt_cloud.cli(args=[...]).wait()` |

Метод `.stream()` обрабатывает события по мере выполнения локального процесса dbt. Метод `.wait()` опрашивает API dbt Cloud до завершения удалённого задания, затем возвращает результаты. Локального процесса для потокового чтения здесь нет.

`DagsterDbtTranslator` работает одинаково в обоих вариантах.

---

## Настройка интеграции с dbt Cloud

### 1. Учётные данные и рабочее пространство

```python
import os
import dagster as dg
from dagster_dbt import DbtCloudCredentials, DbtCloudWorkspace

workspace = DbtCloudWorkspace(
    credentials=DbtCloudCredentials(
        account_id=int(os.environ["DBT_CLOUD_ACCOUNT_ID"]),
        token=os.environ["DBT_CLOUD_API_TOKEN"],
        access_url="https://cloud.getdbt.com",  # your dbt Cloud URL
    ),
    project_id=int(os.environ["DBT_CLOUD_PROJECT_ID"]),
    environment_id=int(os.environ["DBT_CLOUD_ENVIRONMENT_ID"]),
)
```

Значения `account_id` и `project_id` можно найти в URL dbt Cloud. `environment_id` — идентификатор окружения развёртывания, которое должен использовать Dagster.

### 2. Определение ассетов через @dbt_cloud_assets

```python
from dagster_dbt import dbt_cloud_assets

@dbt_cloud_assets(workspace=workspace)
def my_dbt_cloud_assets(
    context: dg.AssetExecutionContext,
    dbt_cloud: DbtCloudWorkspace,
):
    yield from dbt_cloud.cli(args=["build"], context=context).wait()
```

В теле функции используется `dbt_cloud.cli(...).wait()` вместо `dbt.cli(...).stream()`. Именованный аргумент `args` принимает те же команды dbt, которые вы передали бы в терминале.

### 3. Регистрация в Definitions

```python
defs = dg.Definitions(
    assets=[my_dbt_cloud_assets],
    resources={"dbt_cloud": workspace},
)
```

---

## Партиционированные ассеты dbt Cloud

Переменные партиций передаются так же, как через CLI: аргументом `--vars` со словарём в формате JSON.

```python
import json

@dbt_cloud_assets(
    workspace=workspace,
    partitions_def=dg.DailyPartitionsDefinition(start_date="2024-01-01"),
)
def my_partitioned_dbt_cloud_assets(
    context: dg.AssetExecutionContext,
    dbt_cloud: DbtCloudWorkspace,
):
    time_window = context.partition_time_window
    dbt_vars = {
        "min_date": time_window.start.isoformat(),
        "max_date": time_window.end.isoformat(),
    }
    yield from dbt_cloud.cli(
        args=["build", "--vars", json.dumps(dbt_vars)],
        context=context,
    ).wait()
```

---

## Собственный транслятор для dbt Cloud

Передайте экземпляр `DagsterDbtTranslator` в декоратор так же, как при работе через CLI:

```python
@dbt_cloud_assets(
    workspace=workspace,
    dagster_dbt_translator=CustomizedDagsterDbtTranslator(),
)
def my_dbt_cloud_assets(
    context: dg.AssetExecutionContext,
    dbt_cloud: DbtCloudWorkspace,
):
    yield from dbt_cloud.cli(args=["build"], context=context).wait()
```

---

## Когда выбирать dbt Cloud, а когда CLI dbt

Используйте **интеграцию с CLI**, если:

- Самостоятельно запускаете dbt Core на своей инфраструктуре или в CI/CD.
- Хотите полностью управлять выполнением dbt через Dagster.
- Нужен подробный контроль команд, селекторов и переменных во время выполнения.

Используйте **интеграцию с dbt Cloud**, если:

- Проектом и окружениями управляет dbt Cloud.
- Хотите оркестрировать dbt Cloud вместе с остальными шагами пайплайна через Dagster.
- Команда настраивает dbt через интерфейс dbt Cloud.
