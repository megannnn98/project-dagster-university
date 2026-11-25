---
title: "Урок 1: Как модели dbt связаны с ассетами Dagster?"
module: 'dbt_dagster'
lesson: '1'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Как модели dbt связаны с ассетами Dagster?

Модели dbt _являются_ ассетами: они создают данные и могут иметь зависимости. Благодаря этому сходству Dagster может представить каждую модель dbt как [программно определяемый ассет](https://docs.dagster.io/concepts/assets/software-defined-assets) (SDA).

Как Dagster это делает? Каждому компоненту ассета Dagster соответствует элемент модели dbt:

- **Ключ ассета** для модели dbt — по умолчанию имя модели
- **Вышестоящие зависимости** модели dbt определяются вызовами **`ref`** или **`source`** внутри определения модели
- **Вычисление**, необходимое для получения ассета из его вышестоящих зависимостей, задаётся SQL-кодом в определении модели

Рассмотрим следующий код:

```python
from pathlib import Path

from dagster_dbt import DbtCliResource, dbt_assets, get_asset_key_for_model
from dagster_fivetran import build_fivetran_assets

from dagster import AssetExecutionContext, asset

fivetran_assets = build_fivetran_assets(
    connector_id="postgres",
    destination_tables=["users", "orders"],
)


@dbt_assets(manifest=Path("manifest.json"))
def dbt_project_assets(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


@dg.asset(
    kinds={"tensorflow"},
    deps=[get_asset_key_for_model([dbt_project_assets], "daily_order_summary")],
)
def predicted_orders():
    ...
```

Разберём, что происходит в этом примере:

- С помощью `build_fivetran_assets` мы загружаем две таблицы (`users`, `orders`) из коннектора Postgres в Fivetran как ассеты Dagster
- С помощью `@dbt_assets` Dagster читает файл `manifest.json` проекта dbt и создаёт ассеты Dagster из найденных моделей dbt
- Наконец, мы создаём ассет Dagster `@dg.asset` с именем `predicted_orders`, который зависит от вышестоящего ассета dbt с именем `daily_order_summary`
