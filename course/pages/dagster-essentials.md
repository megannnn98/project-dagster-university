---
title: Dagster Essentials
---

- Урок 1: Введение
  - [Что такое инженерия данных?](/dagster-essentials/lesson-1/0-whats-data-engineering)
  - [Что такое оркестратор?](/dagster-essentials/lesson-1/1-whats-an-orchestrator)
  - [Подходы к оркестрации](/dagster-essentials/lesson-1/2-orchestration-approaches)
  - [Чем оркестрация, ориентированная на ассеты, полезна для инженерии данных?](/dagster-essentials/lesson-1/3-why-is-asset-centric-orchestration-good-for-data-engineering)
  - [Знакомство с проектом](/dagster-essentials/lesson-1/4-project-preview)

- Урок 2: Требования и установка
  - [Требования](/installation/requirements)
  - [Локальная настройка](/installation/set-up-local)
  - [Настройка Codespace](/installation/set-up-codespace)
  - [Файлы проекта](/dagster-essentials/lesson-2/3-project-files)

- Урок 3: Программно определяемые ассеты (SDA)
  - [Обзор](/dagster-essentials/lesson-3/0-overview)
  - [Что такое ассет?](/dagster-essentials/lesson-3/1-whats-an-asset)
  - [Определение первого ассета](/dagster-essentials/lesson-3/2-defining-your-first-asset)
  - [Материализация ассета](/dagster-essentials/lesson-3/3-asset-materialization)
  - [Просмотр сведений о запуске](/dagster-essentials/lesson-3/4-viewing-run-details)
  - [Устранение ошибок запуска](/dagster-essentials/lesson-3/5-troubleshooting-failed-runs)
  - [Практика: создание ассета taxi_zones_file](/dagster-essentials/lesson-3/6-coding-practice-taxi-zones-file-asset)
  - [Итоги](/dagster-essentials/lesson-3/7-recap)

- Урок 4: Зависимости ассетов
  - [Обзор](/dagster-essentials/lesson-4/0-overview)
  - [Что такое зависимость?](/dagster-essentials/lesson-4/1-whats-a-dependency)
  - [Ассеты и вычисления в базе данных](/dagster-essentials/lesson-4/2-assets-and-database-execution)
  - [Загрузка данных в базу данных](/dagster-essentials/lesson-4/3-loading-data-into-a-database)
  - [Практика: создание ассета taxi_zones](/dagster-essentials/lesson-4/4-coding-practice-taxi-zones-asset)
  - [Ассеты с вычислениями в оперативной памяти](/dagster-essentials/lesson-4/5-assets-with-in-memory-computations)
  - [Практика: создание ассета trips_by_week](/dagster-essentials/lesson-4/6-coding-practice-trips-by-week-asset)

- Урок 5: Definitions и расположения кода
  - [Обзор](/dagster-essentials/lesson-5/0-overview)
  - [Что такое объект Definitions?](/dagster-essentials/lesson-5/1-whats-the-definitions-object)
  - [Что такое расположение кода?](/dagster-essentials/lesson-5/2-whats-a-code-location)
  - [Расположения кода в интерфейсе Dagster](/dagster-essentials/lesson-5/3-code-locations-dagster-ui)

- Урок 6: Ресурсы
  - [Обзор](/dagster-essentials/lesson-6/0-overview)
  - [Что такое ресурс?](/dagster-essentials/lesson-6/1-whats-a-resource)
  - [Настройка ресурса базы данных](/dagster-essentials/lesson-6/2-setting-up-a-database-resource)
  - [Использование ресурсов в ассетах](/dagster-essentials/lesson-6/3-using-resources-in-assets)
  - [Практика: рефакторинг ассетов для использования ресурсов](/dagster-essentials/lesson-6/4-coding-practice-refactoring-assets)
  - [Анализ использования ресурсов через интерфейс Dagster](/dagster-essentials/lesson-6/5-analyzing-resources-dagster-ui)
  - [Итоги урока](/dagster-essentials/lesson-6/6-recap)

- Урок 7: Расписания
  - [Обзор](/dagster-essentials/lesson-7/0-overview)
  - [Что такое расписания?](/dagster-essentials/lesson-7/1-what-are-schedules)
  - [Практика: создание weekly_update_job](/dagster-essentials/lesson-7/2-coding-practice-weekly-update-job)
  - [Создание расписания](/dagster-essentials/lesson-7/3-creating-a-schedule)
  - [Практика: создание weekly_update_schedule](/dagster-essentials/lesson-7/4-coding-practice-weekly-update-schedule)
  - [Обновление объекта Definitions](/dagster-essentials/lesson-7/5-updating-the-definitions-object)
  - [Задания и расписания в интерфейсе Dagster](/dagster-essentials/lesson-7/6-jobs-schedules-dagster-ui)

- Урок 8: Партиции и backfill
  - [Обзор](/dagster-essentials/lesson-8/0-overview)
  - [Что такое партиции и backfill?](/dagster-essentials/lesson-8/1-what-are-partitions-and-backfills)
  - [Создание партиции](/dagster-essentials/lesson-8/2-creating-a-partition)
  - [Практика: создание недельной партиции](/dagster-essentials/lesson-8/3-coding-practice-weekly-partition)
  - [Добавление партиций к ассетам](/dagster-essentials/lesson-8/4-adding-partitions-to-assets)
  - [Практика: партиционирование ассета taxi_trips](/dagster-essentials/lesson-8/5-coding-practice-partition-taxi-trips)
  - [Создание расписания с партициями по дате](/dagster-essentials/lesson-8/6-creating-a-schedule-with-a-date-based-partition)
  - [Практика: партиционирование ассета trips_by_week](/dagster-essentials/lesson-8/7-coding-practice-partition-trips-by-week)
  - [Партиции и backfill в интерфейсе Dagster](/dagster-essentials/lesson-8/8-partitions-backfills-dagster-ui)
  - [Итоги](/dagster-essentials/lesson-8/9-recap)

- Урок 9: Сенсоры
  - [Обзор](/dagster-essentials/lesson-9/0-overview)
  - [Что такое сенсор?](/dagster-essentials/lesson-9/1-whats-a-sensor)
  - [Настройка создания ассета](/dagster-essentials/lesson-9/2-configuring-asset-creation)
  - [Создание ассета, запускаемого сенсором](/dagster-essentials/lesson-9/3-creating-an-asset-triggered-by-a-sensor)
  - [Создание задания](/dagster-essentials/lesson-9/4-creating-a-job)
  - [Создание сенсора](/dagster-essentials/lesson-9/5-building-the-sensor)
  - [Обновление объекта Definitions](/dagster-essentials/lesson-9/6-updating-the-definitions-object)
  - [Сенсоры в интерфейсе Dagster](/dagster-essentials/lesson-9/7-sensors-dagster-ui)
  - [Включение сенсора](/dagster-essentials/lesson-9/8-enabling-the-sensor)

- Урок 10: Dagster Skills
  - [Разработка с ИИ с помощью Dagster Skills](/shared/dagster-skills)

- [Итоговый проект](/dagster-essentials/capstone)

- Дополнительный раздел: Метаданные
  - [Обзор](/dagster-essentials/extra-credit/0-overview)
  - [Что такое метаданные?](/dagster-essentials/extra-credit/1-whats-metadata)
  - [Метаданные определения — описания ассетов](/dagster-essentials/extra-credit/2-definition-metadata-asset-descriptions)
  - [Метаданные определения — группы ассетов](/dagster-essentials/extra-credit/3-definition-metadata-asset-groups)
  - [Практика: группировка ассетов](/dagster-essentials/extra-credit/4-coding-practice-grouping-assets)
  - [Метаданные материализации](/dagster-essentials/extra-credit/5-materialization-metadata)
  - [Практика: добавление метаданных в taxi_zones_file](/dagster-essentials/extra-credit/6-coding-practice-metadata-taxi-zones-file)
  - [Метаданные ассета в формате Markdown](/dagster-essentials/extra-credit/7-asset-metadata-as-markdown)

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
