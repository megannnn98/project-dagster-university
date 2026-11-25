---
title: 'Урок 2: Создание проекта без скилла'
module: 'ai_driven_data_engineering'
lesson: '2'
---

# Создание проекта без скилла

Сначала создадим проект Dagster без дополнительных скиллов и контекста. Это даст базовый результат для сравнения: что делает способный агент без специальных рекомендаций по Dagster.

## Создание структуры проекта

В этом разделе используется то же имя проекта (`university`), что и в уроке 4. Если выполняешь упражнение, перед началом урока 4 удали этот учебный каталог (или перенеси его в другое место), чтобы избежать конфликта.

Используй общий промпт, например:

```text
create a new Dagster project called university
```

![Без скилла: первый запрос](/images/ai-driven-data-engineering/lesson-2/without-1.png)

Агент выяснит, как создать проект Dagster, и может выполнить что-то подобное:

```bash
dagster project scaffold --name university
```

Здесь используется устаревшая команда CLI `dagster project scaffold`, создающая плоскую структуру (например, `university/university/` с файлами `__init__.py`, `assets.py` и `definitions.py`).

## Генерация ассетов

Далее попроси агента добавить ассеты, загружающие данные в DuckDB из внешних CSV по URL:

```text
create 3 assets in the university Dagster project that load data into DuckDB tables for the following external files:

https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_customers.csv
https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_orders.csv
https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_payments.csv
```

Агент добавит код (часто в `assets.py` или аналогичный файл) и может использовать или не использовать `dagster-duckdb` и правильную структуру проекта. Ты получишь работающий пайплайн, но структура и инструменты будут зависеть от предположений модели.

## Результат

После создания структуры проекта и добавления ассетов он может выглядеть так:

```text
tree university/university

university/university
├── __init__.py
├── assets.py
└── definitions.py
```

Когда агенту программирования не предоставляют дополнительных скиллов или специфического контекста, он часто использует общие шаблоны, с которыми уже сталкивался, а не лучшие или наиболее идиоматичные практики конкретного инструмента. Это ограничение характерно не только для Dagster: агенты обычно создают более качественные и надёжные решения, когда получают рекомендации, адаптированные к технологии или задаче. Без дополнительных подсказок результат может быть функциональным, но обычно менее продуманным, удобным в сопровождении и соответствующим экспертным практикам.

![Структура проекта без скиллов](/images/ai-driven-data-engineering/lesson-2/project-without-skills.png)

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
