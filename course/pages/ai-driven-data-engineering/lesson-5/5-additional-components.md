---
title: 'Урок 5: Дополнительные компоненты'
module: 'ai_driven_data_engineering'
lesson: '5'
---

# Дополнительные компоненты

Слой преобразования готов, но dbt, вероятно, не единственная интеграция твоей платформы данных. Допустим, нужно также передать данные из DuckDB в системы, которыми пользуются нижестоящие потребители. В данном случае нужно экспортировать данные `fct_orders` в S3 в формате Parquet.

Можно написать отдельный ассет, выполняющий запрос DuckDB и загружающий результат в S3. Это сработает. Но лучше использовать полноценный механизм репликации, который аккуратно выполняет необходимые операции и обеспечивает структуру компонента, согласованную с остальным проектом. Скилл `dagster-expert` поможет определить подход.

## Запрашиваем варианты у агента

Если не уверен, какую интеграцию использовать, просто спроси:

```text
/dagster-expert I would like to export the data from the fct_orders model to S3. What are some good open-source tools that can handle this with Dagster?
```

Вместо возврата кода агент поделится соображениями о возможных решениях:

```text
For exporting from DuckDB to S3, there are two strong open-source options with first-class
  Dagster support:

  ---
  Sling (dagster-sling) — Recommended for this use case

  Sling is purpose-built for data replication between databases and file systems, including
  DuckDB → S3. It's the most direct fit here.

  - Reads directly from DuckDB and writes to S3 as CSV, Parquet, JSON, etc.
  - Component-based Dagster integration with a simple YAML config
  - Low complexity, high performance
  - Open-source CLI tool

  # replication config example
  source: DUCKDB
  target: S3

  streams:
    main.fct_orders:
      object: s3://my-bucket/exports/fct_orders.parquet
      mode: full-refresh

  ---
  dlt (dagster-dlt) — Best if you need schema evolution or incremental loads

  dlt is a Python-native EL library that handles schema inference, incremental state, and
  normalization. It supports DuckDB as a source and S3 as a destination.

  - More code-centric than Sling (Python-based pipeline definitions)
  - Strong incremental loading with built-in state management
  - Good fit if the export logic needs transformation or filtering in Python
  - Open-source

  ---
  Quick comparison for your case

  ┌─────────────────────┬─────────────────┬─────────────────┐
  │                     │      Sling      │       dlt       │
  ├─────────────────────┼─────────────────┼─────────────────┤
  │ DuckDB → S3         │ ✅ Native       │ ✅ Supported    │
  ├─────────────────────┼─────────────────┼─────────────────┤
  │ Config style        │ YAML            │ Python          │
  ├─────────────────────┼─────────────────┼─────────────────┤
  │ Incremental         │ ✅              │ ✅ Strong       │
  ├─────────────────────┼─────────────────┼─────────────────┤
  │ Complexity          │ Low             │ Medium          │
  ├─────────────────────┼─────────────────┼─────────────────┤
  │ Dagster integration │ Component-based │ Component-based │
  └─────────────────────┴─────────────────┴─────────────────┘

  Recommendation: Start with Sling — it's the least overhead for a straightforward DuckDB → S3
   export and integrates cleanly as a Dagster component alongside your existing dbt setup.
  Would you like to implement one of these?
```

Это именно то, для чего создан экспертный скилл: ты описал цель, а он сузил пространство решений до двух хорошо поддерживаемых вариантов с конкретной рекомендацией. Тебе не нужно было знать о существовании [Sling](https://slingdata.io/) или [dlt](https://dlthub.com/context/).

## Настройка компонента Sling

На основании рекомендации агента попробуем Sling. Попроси агента подключить Sling и экспортировать таблицу fct_orders в S3:

```text {% obfuscated="true" %}
/dagster-expert Setup a Sling component that exports the DuckDB data from fct_orders to S3 (assume the bucket is called test-bucket).
```

Этот рабочий процесс уже должен быть знаком. Агент управляет зависимостью, создаёт заготовку компонента и настраивает репликацию, а затем проверяет успешность:

```bash
uv add dagster-sling
```

```bash
dg scaffold defs dagster_sling.SlingReplicationCollectionComponent fct_orders_s3_export
```

```bash
dg check defs
```

Компонент Sling похож на компонент dbt, однако у каждого своя специфическая конфигурация. Одно из отличий: для компонента Sling требуется дополнительный конфигурационный файл, определяющий сведения об источнике (`source`) и назначении (`target`). Агент обрабатывает всё это и помещает информацию из промпта в правильные места.

Перед материализацией ассета Sling необходимы реальные учётные данные AWS или локальное S3-совместимое хранилище. Если у тебя нет аккаунта AWS, см. раздел [Локальное тестирование с MinIO](#testing-locally-with-minio) в конце страницы.

```yaml
# /src/university/defs/fct_orders_s3_export/replication.yaml
source: DUCKDB
target: S3

streams:
  "main.fct_orders":
    object: "s3://test-bucket/fct_orders.parquet"
    mode: full-refresh
```

## Настройка зависимости

В промпте мы не указали явно зависимость нашего ассета. Если посмотреть на каталог ассетов, можно обнаружить, что ассет Sling отсоединён от остальных. Это легко исправить:

```text {% obfuscated="true" %}
/dagster-expert The parquet asset should have a dependency on the fct_orders asset.
```

Агент настраивает зависимость. Теперь полный граф корректен: исходные ассеты → staging-модели dbt → `fct_orders` → экспорт Parquet в S3. Можно запустить весь пайплайн одной командой, и всё материализуется в правильном порядке.

![Граф ассетов с dbt и экспортом Sling в S3](/images/ai-driven-data-engineering/lesson-5/project-dbt-sling.png)

Открой каталог ассетов и посмотри на результат. Это полный ELT-пайплайн из обзора проекта, построенный с помощью промптов, без ручного создания структуры проекта и чтения документации Sling.

<a id="testing-locally-with-minio"></a>

## Локальное тестирование с MinIO

Для материализации ассета Sling нужны учётные данные AWS и бакет S3 либо их локальный совместимый аналог. Для локального тестирования без аккаунта AWS в репозитории курса предусмотрена настройка S3 на основе MinIO. MinIO — S3-совместимое объектное хранилище, запускаемое в Docker.

Возьми `docker-compose.yaml` из репозитория курса: `dagster_university/ai_driven_data_engineering/docker-compose.yaml` ([посмотреть на GitHub](https://github.com/dagster-io/project-dagster-university/blob/main/dagster_university/ai_driven_data_engineering/docker-compose.yaml)). Помести его в удобный каталог и выполни:

```bash
docker compose up -d
```

Это создаёт бакет `test-bucket` по адресу `http://localhost:9000` с учётными данными `minioadmin` / `minioadmin`. Настрой компонент Sling на использование этой конечной точки вместо AWS. Попроси агента обновить конфигурацию ресурса:

```text
/dagster-expert Update the Sling resource to use a local MinIO endpoint at http://localhost:9000 with access key minioadmin and secret key minioadmin.
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
