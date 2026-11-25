---
title: "Практика: Группировка моделей dbt по слоям"
module: 'dagster_essentials'
lesson: '5'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Практика: Группировка моделей dbt по слоям

Переопределите метод `get_group_name` в `CustomizedDagsterDbtTranslator`, чтобы группировать модели dbt по слоям (`marts` и `staging`).

**Подсказка:** `dbt_resource_props` — словарь Python примерно такой структуры:

```json
{
    "database": "data",
    "schema": "main",
    "name": "stg_trips",
    "resource_type": "model",
    "package_name": "analytics",
    "path": "staging/stg_trips.sql",
    "original_file_path": "models/staging/stg_trips.sql",
    "unique_id": "model.analytics.stg_trips",
    "fqn": ["analytics", "staging", "stg_trips"],
    "alias": "stg_trips",
    ... #other properties
}
```

Метод `get_group_name` должен вернуть строку с именем группы. Какое свойство `dbt_resource_props` можно использовать, возможно обратившись к элементу по индексу, чтобы получить слой модели, например `marts` или `staging`?

---

## Проверка решения

Ваш метод должен выглядеть примерно так. Нажмите **View answer**, чтобы увидеть ответ:

```python {% obfuscated="true" %}
def get_group_name(self, dbt_resource_props):
    return dbt_resource_props["fqn"][1]
```
