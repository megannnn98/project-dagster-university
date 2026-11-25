---
title: "Урок 1: Зачем использовать dbt и Dagster вместе?"
module: 'dbt_dagster'
lesson: '1'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Зачем использовать dbt и Dagster вместе?

На первый взгляд может показаться, что Dagster и dbt выполняют одну и ту же работу. Обе технологии работают с ассетами данных и играют важную роль в современных платформах данных.

Однако dbt Core может лишь преобразовывать данные, уже находящиеся в хранилище: он не извлекает их из источника, не загружает в конечное хранилище и не автоматизирует эти операции. Хотя встроенные возможности dbt Cloud позволяют запускать модели по расписанию, другие части пайплайнов данных, например таблицы, загруженные через Fivetran, или данные из Amazon S3, останутся за пределами этого процесса.

Чтобы все компоненты работали вместе, нужен оркестратор. Здесь на помощь приходит Dagster.

Цитата из оригинала:

> Dagster’s core design principles go really well together with dbt. The similarities between the way that Dagster thinks about data pipelines and the way that dbt thinks about data pipelines means that Dagster can orchestrate dbt much more faithfully than other general-purpose orchestrators like Airflow.
>
> At the same time, Dagster is able to compensate for dbt’s biggest limitations. dbt is rarely used in a vacuum: the data transformed using dbt needs to come from somewhere and go somewhere. When a data platform needs more than just dbt, Dagster is a better fit than dbt-specific orchestrators, like the job scheduling system inside dbt Cloud. ([source](https://dagster.io/blog/orchestrating-dbt-with-dagster))

Совместное использование dbt и Dagster даёт инженерам аналитики и инженерам данных преимущества обоих подходов:

- **Инженеры аналитики** могут писать аналитический код на знакомом языке, соблюдая лучшие практики разработки ПО.
- **Инженеры данных** могут легко интегрировать dbt в общую платформу данных организации, обеспечивая наблюдаемость и надёжность.

Другие оркестраторы обычно предлагают два не слишком привлекательных варианта: запускать dbt как единственную задачу с ограниченной наблюдаемостью либо запускать каждую модель dbt как отдельную задачу, передавая управление выполнением оркестратору вопреки принципам работы dbt.

Особенность интеграции dbt с Dagster заключается в том, что Dagster отделяет ассеты данных от процесса их создания и позволяет отслеживать и отлаживать каждую модель dbt отдельно.
