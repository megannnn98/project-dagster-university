---
title: "Урок 3: Создание ресурса Dagster для запуска dbt"
module: 'dagster_dbt'
lesson: '3'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Создание ресурса Dagster для запуска dbt

Следующий шаг — определить ресурс Dagster, через который будут запускаться и настраиваться команды dbt.

Основной ресурс, с которым вы будете работать, — `DbtCliResource`. В следующих разделах рассмотрим его методы и настройку действий Dagster при выполнении dbt.

> 💡 **Напоминание о ресурсах:** ресурсы — рекомендуемый в Dagster способ подключения к другим сервисам и инструментам: dbt, хранилищу данных или BI-инструменту.

Откройте `defs/resources.py`, где уже определены другие ресурсы. Мы будем дополнять этот файл.

> ⚠️ **Важно:** в `resources.py` уже есть `database_resource`, `smart_open_config` и другие импорты. Сохраните этот код и добавьте к нему импорты и определение ресурса dbt.

1. В начало файла, рядом с существующими импортами, добавьте:

   ```python
   from dagster_dbt import DbtCliResource

   from dagster_and_dbt.defs.project import dbt_project
   ```

2. После кода `smart_open_config` добавьте определение `dbt_resource`:

   ```python
   dbt_resource = DbtCliResource(
       project_dir=dbt_project,
   )
   ```

3. Обновите функцию с декоратором `@dg.definitions`, включив новый ресурс `dbt`:

   ```python
   @dg.definitions
   def resources():
       return dg.Definitions(
           resources={
               "database": database_resource,
               "dbt": dbt_resource,
           },
       )
   ```

После изменений полный файл `resources.py` должен выглядеть так:

```python
# src/dagster_and_dbt/defs/resources.py
import os

import boto3
import dagster as dg
from dagster_dbt import DbtCliResource
from dagster_duckdb import DuckDBResource

from dagster_and_dbt.defs.project import dbt_project

database_resource = DuckDBResource(
    database=dg.EnvVar("DUCKDB_DATABASE"),
)

if os.getenv("DAGSTER_ENVIRONMENT") == "prod":
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )
    smart_open_config = {"client": session.client("s3")}
else:
    smart_open_config = {}


dbt_resource = DbtCliResource(
    project_dir=dbt_project,
)


@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "database": database_resource,
            "dbt": dbt_resource,
        },
    )
```

Добавленный код:

1. Импортирует `DbtCliResource` из установленного ранее пакета `dagster_dbt`.
2. Импортирует созданное представление `dbt_project`.
3. Создаёт экземпляр `DbtCliResource` под именем `dbt_resource`.
4. Указывает ресурсу, что запускать нужно проект `dbt_project`.
5. Добавляет ресурс в определения для автоматической загрузки.
