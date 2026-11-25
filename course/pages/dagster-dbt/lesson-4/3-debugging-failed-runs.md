---
title: "Урок 4: Отладка неудачных запусков"
module: 'dagster_dbt'
lesson: '4'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Отладка неудачных запусков

Инженерам данных часто приходится разбирать сбои, поэтому важно уметь отлаживать шаг выполнения dbt.

Намеренно внесём ошибку в модель dbt, увидим сбой в Dagster, найдём его причину и повторно запустим пайплайн. Отладка ассетов dbt во многом похожа на отладку dbt при самостоятельном использовании.

1. Откройте `stg_zones.sql` и добавьте столбец `zone_population` в выражение `select`:

   ```sql
   with raw_zones as (
       select *
       from {{ source('raw_taxis', 'zones') }}
   )
   select
       zone_id,
       zone as zone_name,
       borough,
       zone_name like '%Airport' as is_airport,
       zone_population -- new column
   from raw_zones
   ```

2. В интерфейсе Dagster перезагрузите расположение кода кнопкой **Reload Definitions** или сочетанием **Option+Shift+R**.
3. Найдите в графе ассет `stg_zones`. Жёлтая метка **Code version** показывает, что Dagster обнаружил изменение SQL:

   ![Ассет stg_zones с меткой версии кода в Dagster](/images/dagster-dbt/lesson-4/stg-zones-code-version.png)

4. Выберите `stg_zones` и нажмите **Materialize**.
5. Перейдите к странице сведений о запуске.
6. Нажмите шаг `dbt_analytics`:

   ![Журнал stdout с ошибкой материализации stg_zones](/images/dagster-dbt/lesson-4/stg-zones-stdout-failure.png)

Из журнала видно, что DuckDB не может найти столбец `zone_population`: такого столбца нет в исходных данных.

Исправим ошибку:

1. Удалите `zone_population` из модели `stg_zones`.
2. Перезагрузите расположение кода в Dagster, чтобы применить изменения.

Повторная материализация `stg_zones` теперь должна завершиться успешно.
