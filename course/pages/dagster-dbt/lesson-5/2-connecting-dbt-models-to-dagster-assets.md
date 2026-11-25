---
title: "Урок 5: Связывание моделей dbt с ассетами Dagster"
module: 'dagster_dbt'
lesson: '5'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Связывание моделей dbt с ассетами Dagster

## Нужен ли собственный транслятор?

Это зависит от того, совпадают ли имена источников dbt с ключами существующих ассетов Dagster.

Класс `DagsterDbtTranslator` управляет тем, как Dagster интерпретирует узлы проекта dbt: модели, источники, seed и snapshot. Он задаёт ключи ассетов, группы, теги и метаданные. По умолчанию модель `stg_trips` получает ключ `stg_trips`, а источник `trips` из `raw_taxis` — ключ `raw_taxis/trips`.

**Стандартного транслятора достаточно**, если проект dbt самостоятельный и имена его источников уже соответствуют ключам ассетов. Это часто бывает в новых проектах, где Dagster и dbt настраиваются одновременно.

**Собственный транслятор нужен**, когда:

- Имена источников dbt не соответствуют существующим ключам Dagster. Именно это мы исправим: ассет Dagster называется `taxi_trips`, а ключ источника dbt по умолчанию — `raw_taxis/trips`.
- Нужно распределять модели по группам ассетов на основе каталогов, тегов или типов материализации dbt. Такой пример есть в практическом задании в конце урока.
- Нужно добавлять единообразные теги или метаданные всем ассетам dbt.

Переопределяйте только необходимые методы, а в остальных случаях используйте `super()`. В [справочнике API](https://docs.dagster.io/_apidocs/libraries/dagster-dbt#dagster_dbt.DagsterDbtTranslator) перечислены доступные методы: `get_asset_key`, `get_group_name`, `get_tags`, `get_metadata` и другие.

---

Источники проекта dbt — это таблицы DuckDB, созданные ассетами Dagster. Однако использующие их staging-модели (`stg_trips`, `stg_zones`) пока не связаны с ассетами (`taxi_trips`, `taxi_zones`), которые создали эти таблицы:

![Модели dbt без связей с ассетами Dagster](/images/dagster-dbt/lesson-5/unconnected-sources-assets.png)

Сообщим Dagster, что источники dbt соответствуют таблицам, создаваемым определениями `taxi_trips` и `taxi_zones`. Для этого сопоставим ключи ассетов. При совпадении ключей Dagster объединит представления одного и того же ассета.

Например, исходный ключ источника dbt — `raw_taxis/trips`, а ключ создающего таблицу ассета Dagster — `taxi_trips`. Изменим ключ источника dbt на `taxi_trips`.

Правила преобразования узлов проекта dbt в ассеты интеграция `dagster-dbt` задаёт через `DagsterDbtTranslator`.

---

## Настройка интерпретации проекта dbt

Dagster вызывает методы `DagsterDbtTranslator` для узлов проекта и использует возвращаемые значения при настройке ассетов.

Чтобы изменить правила, создайте класс-наследник и переопределите нужные методы. Подробности — в [справочнике API](https://docs.dagster.io/_apidocs/libraries/dagster-dbt#dagster_dbt.DagsterDbtTranslator) пакета `dagster-dbt`.

Сейчас переопределим `get_asset_key`, управляющий ключами ассетов.

Откройте `defs/assets/dbt.py`:

1. Добавьте импорт `DagsterDbtTranslator` из `dagster_dbt`. Класс `AssetKey` доступен через уже импортированный модуль `dagster` под именем `dg`.
2. После импортов создайте класс `CustomizedDagsterDbtTranslator`, наследующий `DagsterDbtTranslator`:

   ```python
   class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
   ```

3. Определите в классе метод `get_asset_key`.

   Это метод экземпляра, поэтому первым параметром будет `self` согласно [соглашениям Python](https://builtin.com/software-engineering-perspectives/python-guide). Второй параметр, `dbt_resource_props`, — словарь свойств узла dbt из манифеста. Метод должен возвращать объект `AssetKey`.

    ```python
    class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
        def get_asset_key(self, dbt_resource_props):
    ```

4. Реализуйте собственные правила формирования ключей:

   1. Получите свойства `resource_type` (например, model, source, seed или snapshot) и `name` (например, `trips` или `stg_trips`) из `dbt_resource_props` и сохраните в `resource_type` и `name`:

      ```python
      def get_asset_key(self, dbt_resource_props):
          resource_type = dbt_resource_props["resource_type"]
          name = dbt_resource_props["name"]
      ```

   2. Существующие ассеты Dagster называются `taxi_trips` и `taxi_zones`, а источники dbt — `trips` и `zones`. Для совпадения ключей добавим префикс `taxi_`:

      ```python
      def get_asset_key(self, dbt_resource_props):
          resource_type = dbt_resource_props["resource_type"]
          name = dbt_resource_props["name"]
      
          return dg.AssetKey(f"taxi_{name}")
      ```

   3. Переименовывать нужно только источники, сохранив стандартные ключи моделей. Воспользуемся `super()`, чтобы для остальных узлов вызвать реализацию родительского класса:

      ```python
      def get_asset_key(self, dbt_resource_props):
          resource_type = dbt_resource_props["resource_type"]
          name = dbt_resource_props["name"]
          if resource_type == "source":
              return dg.AssetKey(f"taxi_{name}")
          else:
              return super().get_asset_key(dbt_resource_props)
      ```

      Первый собственный транслятор готов.

      {% callout %}
      > 💡 **Важно:** ключи ассетов Dagster должны быть уникальны. Если возникает `DuplicateKeyError`, добавьте журналирование и проверьте, не возвращает ли `get_asset_key` один и тот же ключ для разных узлов.
      {% /callout %}

5. Передайте экземпляр `CustomizedDagsterDbtTranslator` в аргумент `dagster_dbt_translator` декоратора `@dbt_assets`. **Обязательно создайте экземпляр класса**, добавив скобки:

   ```python
   @dbt_assets(
       manifest=dbt_project.manifest_path,
       dagster_dbt_translator=CustomizedDagsterDbtTranslator()
   )
   def dbt_analytics(context: dg.AssetExecutionContext, dbt: DbtCliResource):
       yield from dbt.cli(["build"], context=context).stream()
   ```

Полный файл `defs/assets/dbt.py` должен выглядеть так:

```python
# src/dagster_and_dbt/defs/assets/dbt.py
import dagster as dg
from dagster_dbt import DagsterDbtTranslator, DbtCliResource, dbt_assets

from dagster_and_dbt.defs.project import dbt_project


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
)
def dbt_analytics(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
```
