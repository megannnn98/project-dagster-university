---
title: "Урок 3: Подготовка проекта dbt"
module: 'dagster_dbt'
lesson: '3'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Подготовка проекта dbt

Вне зависимости от Dagster большинство команд dbt создаёт набор файлов в новом каталоге `target`. Самый важный из них — `manifest.json`, обычно называемый файлом манифеста. [Этот файл](https://docs.getdbt.com/reference/artifacts/manifest-json) содержит полное описание проекта dbt в предсказуемом формате.

При загрузке расположения кода Dagster читает манифест, обнаруживает модели dbt и превращает их в ассеты Dagster. Создать `manifest.json` можно разными способами; мы рекомендуем команду `dbt parse`.

Перейдите в каталог `dagster_university/dagster_and_dbt/src/dagster_and_dbt/analytics` и выполните:

```bash
cd dagster_university/dagster_and_dbt/src/dagster_and_dbt/analytics # if you haven't set the directory yet
dbt parse
```

Убедитесь, что появились:

1. Каталог `dagster_university/dagster_and_dbt/src/dagster_and_dbt/analytics/target`.
2. Файл `manifest.json` внутри `target`.

{% callout %}
> 💡 Мы рекомендуем `dbt parse`, потому что, в отличие от таких команд, как `dbt compile`, для создания манифеста ей не требуется подключение к хранилищу данных. Это обеспечивает быструю и предсказуемую работу как локально, так и при развёртывании.
>
> Если модели dbt используют [запросы для анализа структуры данных](https://docs.getdbt.com/reference/commands/compile#interactive-compile), может потребоваться `dbt compile`.
{% /callout %}

В четвёртом уроке рассмотрим автоматическую подготовку манифеста при разработке; в седьмом — его создание при развёртывании.
