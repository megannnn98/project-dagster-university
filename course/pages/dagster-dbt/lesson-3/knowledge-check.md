---
title: "Проверка знаний"
module: 'dagster_essentials'
lesson: '3'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Проверка знаний

Команда `dbt run` выполняет модели. Команда `dbt build` дополнительно выполняет тесты dbt в нужном порядке и останавливает зависимые действия при неуспешной проверке. Обычно стоит начинать с `dbt build`, чтобы вместе с выполнением моделей получать проверки качества данных.

1. Откройте `defs/assets/dbt.py`.
2. Измените `dbt_analytics`, чтобы функция выполняла `dbt build` вместо `dbt run`:

   ```python
   # src/dagster_and_dbt/defs/assets/dbt.py
   @dbt_assets(
       manifest=dbt_project.manifest_path
   )
   def dbt_analytics(context: dg.AssetExecutionContext, dbt: DbtCliResource):
       yield from dbt.cli(["build"], context=context).stream()
   ```

3. В интерфейсе Dagster повторно материализуйте обе модели dbt.
4. Откройте страницу сведений о начавшемся запуске и изучите журнал.

Закончив, переходите к следующей странице.
