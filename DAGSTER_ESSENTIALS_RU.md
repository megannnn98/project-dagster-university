# Dagster Essentials — оглавление на русском

[К списку курсов](README.md) · [Как запустить учебный сайт](course/README.md)

- Урок 1: Введение
  - [Что такое инженерия данных?](course/pages/dagster-essentials/lesson-1/0-whats-data-engineering.md)
  - [Что такое оркестратор?](course/pages/dagster-essentials/lesson-1/1-whats-an-orchestrator.md)
  - [Подходы к оркестрации](course/pages/dagster-essentials/lesson-1/2-orchestration-approaches.md)
  - [Чем оркестрация, ориентированная на активы, полезна для инженерии данных?](course/pages/dagster-essentials/lesson-1/3-why-is-asset-centric-orchestration-good-for-data-engineering.md)
  - [Знакомство с проектом](course/pages/dagster-essentials/lesson-1/4-project-preview.md)

- Урок 2: Требования и установка
  - [Требования](course/pages/installation/requirements.md)
  - [Локальная настройка](course/pages/installation/set-up-local.md)
  - [Настройка Codespace](course/pages/installation/set-up-codespace.md)
  - [Файлы проекта](course/pages/dagster-essentials/lesson-2/3-project-files.md)

- Урок 3: Программно определяемые активы (SDA)
  - [Обзор](course/pages/dagster-essentials/lesson-3/0-overview.md)
  - [Что такое актив?](course/pages/dagster-essentials/lesson-3/1-whats-an-asset.md)
  - [Определение первого актива](course/pages/dagster-essentials/lesson-3/2-defining-your-first-asset.md)
  - [Материализация актива](course/pages/dagster-essentials/lesson-3/3-asset-materialization.md)
  - [Просмотр сведений о запуске](course/pages/dagster-essentials/lesson-3/4-viewing-run-details.md)
  - [Устранение ошибок запуска](course/pages/dagster-essentials/lesson-3/5-troubleshooting-failed-runs.md)
  - [Практика: создание актива taxi_zones_file](course/pages/dagster-essentials/lesson-3/6-coding-practice-taxi-zones-file-asset.md)
  - [Итоги](course/pages/dagster-essentials/lesson-3/7-recap.md)

- Урок 4: Зависимости активов
  - [Обзор](course/pages/dagster-essentials/lesson-4/0-overview.md)
  - [Что такое зависимость?](course/pages/dagster-essentials/lesson-4/1-whats-a-dependency.md)
  - [Активы и вычисления в базе данных](course/pages/dagster-essentials/lesson-4/2-assets-and-database-execution.md)
  - [Загрузка данных в базу данных](course/pages/dagster-essentials/lesson-4/3-loading-data-into-a-database.md)
  - [Практика: создание актива taxi_zones](course/pages/dagster-essentials/lesson-4/4-coding-practice-taxi-zones-asset.md)
  - [Активы с вычислениями в оперативной памяти](course/pages/dagster-essentials/lesson-4/5-assets-with-in-memory-computations.md)
  - [Практика: создание актива trips_by_week](course/pages/dagster-essentials/lesson-4/6-coding-practice-trips-by-week-asset.md)

- Урок 5: Definitions и расположения кода
  - [Обзор](course/pages/dagster-essentials/lesson-5/0-overview.md)
  - [Что такое объект Definitions?](course/pages/dagster-essentials/lesson-5/1-whats-the-definitions-object.md)
  - [Что такое расположение кода?](course/pages/dagster-essentials/lesson-5/2-whats-a-code-location.md)
  - [Расположения кода в интерфейсе Dagster](course/pages/dagster-essentials/lesson-5/3-code-locations-dagster-ui.md)

- Урок 6: Ресурсы
  - [Обзор](course/pages/dagster-essentials/lesson-6/0-overview.md)
  - [Что такое ресурс?](course/pages/dagster-essentials/lesson-6/1-whats-a-resource.md)
  - [Настройка ресурса базы данных](course/pages/dagster-essentials/lesson-6/2-setting-up-a-database-resource.md)
  - [Использование ресурсов в активах](course/pages/dagster-essentials/lesson-6/3-using-resources-in-assets.md)
  - [Практика: рефакторинг активов для использования ресурсов](course/pages/dagster-essentials/lesson-6/4-coding-practice-refactoring-assets.md)
  - [Анализ использования ресурсов через интерфейс Dagster](course/pages/dagster-essentials/lesson-6/5-analyzing-resources-dagster-ui.md)
  - [Итоги урока](course/pages/dagster-essentials/lesson-6/6-recap.md)

- Урок 7: Расписания
  - [Обзор](course/pages/dagster-essentials/lesson-7/0-overview.md)
  - [Что такое расписания?](course/pages/dagster-essentials/lesson-7/1-what-are-schedules.md)
  - [Практика: создание weekly_update_job](course/pages/dagster-essentials/lesson-7/2-coding-practice-weekly-update-job.md)
  - [Создание расписания](course/pages/dagster-essentials/lesson-7/3-creating-a-schedule.md)
  - [Практика: создание weekly_update_schedule](course/pages/dagster-essentials/lesson-7/4-coding-practice-weekly-update-schedule.md)
  - [Обновление объекта Definitions](course/pages/dagster-essentials/lesson-7/5-updating-the-definitions-object.md)
  - [Задания и расписания в интерфейсе Dagster](course/pages/dagster-essentials/lesson-7/6-jobs-schedules-dagster-ui.md)

- Урок 8: Партиции и backfill
  - [Обзор](course/pages/dagster-essentials/lesson-8/0-overview.md)
  - [Что такое партиции и backfill?](course/pages/dagster-essentials/lesson-8/1-what-are-partitions-and-backfills.md)
  - [Создание партиции](course/pages/dagster-essentials/lesson-8/2-creating-a-partition.md)
  - [Практика: создание недельной партиции](course/pages/dagster-essentials/lesson-8/3-coding-practice-weekly-partition.md)
  - [Добавление партиций к активам](course/pages/dagster-essentials/lesson-8/4-adding-partitions-to-assets.md)
  - [Практика: партиционирование актива taxi_trips](course/pages/dagster-essentials/lesson-8/5-coding-practice-partition-taxi-trips.md)
  - [Создание расписания с партициями по дате](course/pages/dagster-essentials/lesson-8/6-creating-a-schedule-with-a-date-based-partition.md)
  - [Практика: партиционирование актива trips_by_week](course/pages/dagster-essentials/lesson-8/7-coding-practice-partition-trips-by-week.md)
  - [Партиции и backfill в интерфейсе Dagster](course/pages/dagster-essentials/lesson-8/8-partitions-backfills-dagster-ui.md)
  - [Итоги](course/pages/dagster-essentials/lesson-8/9-recap.md)

- Урок 9: Сенсоры
  - [Обзор](course/pages/dagster-essentials/lesson-9/0-overview.md)
  - [Что такое сенсор?](course/pages/dagster-essentials/lesson-9/1-whats-a-sensor.md)
  - [Настройка создания актива](course/pages/dagster-essentials/lesson-9/2-configuring-asset-creation.md)
  - [Создание актива, запускаемого сенсором](course/pages/dagster-essentials/lesson-9/3-creating-an-asset-triggered-by-a-sensor.md)
  - [Создание задания](course/pages/dagster-essentials/lesson-9/4-creating-a-job.md)
  - [Создание сенсора](course/pages/dagster-essentials/lesson-9/5-building-the-sensor.md)
  - [Обновление объекта Definitions](course/pages/dagster-essentials/lesson-9/6-updating-the-definitions-object.md)
  - [Сенсоры в интерфейсе Dagster](course/pages/dagster-essentials/lesson-9/7-sensors-dagster-ui.md)
  - [Включение сенсора](course/pages/dagster-essentials/lesson-9/8-enabling-the-sensor.md)

- Урок 10: Dagster Skills
  - [Разработка с ИИ с помощью Dagster Skills](course/pages/shared/dagster-skills.md)

- [Итоговый проект](course/pages/dagster-essentials/capstone.md)

- Дополнительный раздел: Метаданные
  - [Обзор](course/pages/dagster-essentials/extra-credit/0-overview.md)
  - [Что такое метаданные?](course/pages/dagster-essentials/extra-credit/1-whats-metadata.md)
  - [Метаданные определения — описания активов](course/pages/dagster-essentials/extra-credit/2-definition-metadata-asset-descriptions.md)
  - [Метаданные определения — группы активов](course/pages/dagster-essentials/extra-credit/3-definition-metadata-asset-groups.md)
  - [Практика: группировка активов](course/pages/dagster-essentials/extra-credit/4-coding-practice-grouping-assets.md)
  - [Метаданные материализации](course/pages/dagster-essentials/extra-credit/5-materialization-metadata.md)
  - [Практика: добавление метаданных в taxi_zones_file](course/pages/dagster-essentials/extra-credit/6-coding-practice-metadata-taxi-zones-file.md)
  - [Метаданные актива в формате Markdown](course/pages/dagster-essentials/extra-credit/7-asset-metadata-as-markdown.md)

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
