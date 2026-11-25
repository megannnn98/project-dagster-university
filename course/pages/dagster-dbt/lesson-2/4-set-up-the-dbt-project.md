---
title: "Урок 2: Настройка проекта dbt"
module: 'dagster_dbt'
lesson: '2'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Настройка проекта dbt

В клонированном репозитории есть проект dbt под названием `analytics`. В ходе курса вы будете добавлять в него модели dbt и видеть их в Dagster.

1. Перейдите в каталог проекта:

    ```bash
    cd dagster_university/dagster_and_dbt/src/dagster_and_dbt/analytics
    ```

2. Установите зависимости из пакетов dbt:

    ```bash
    dbt deps
    ```

3. Откройте каталог `analytics` в файловом менеджере или IDE. В нём должны быть следующие файлы — описания источников и начальные модели:

    - `models/sources/raw_taxis.yml`
    - `models/staging/staging.yml`
    - `models/staging/stg_trips.sql`
    - `models/staging/stg_zones.sql`
