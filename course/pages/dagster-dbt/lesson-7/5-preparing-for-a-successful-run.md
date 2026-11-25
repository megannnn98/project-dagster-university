---
title: "Урок 7: Подготовка к успешному запуску"
module: 'dbt_dagster'
lesson: '7'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Подготовка к успешному запуску

{% callout %}
>💡 **Этот раздел необязателен.** Цель урока — научиться развёртывать проект в Dagster+ — достигнута на предыдущем шаге. Для выполнения пайплайна понадобятся внешние сервисы; вы можете предпочесть другие, поэтому этот раздел вынесен отдельно.
{% /callout %}

В прошлых уроках вы добавляли примеры в локальный проект, материализовали ассеты и сохраняли результаты в локальной базе DuckDB.

Настройка production сложнее. Здесь разберём изменения в пайплайне, необходимые для успешного запуска, предполагая, что внешние хранилища уже настроены и готовы к работе. Сам процесс их создания в раздел не входит.

---

## Обзор развёртывания

Для чтения и записи ассетов в production используем:

- **Amazon S3** вместо локальной файловой системы. В оригинале предполагается небольшой объём данных, укладывающийся в бесплатный тариф AWS; актуальные лимиты и стоимость зависят от условий вашего аккаунта. Пример настройки бакета — в [этом руководстве](https://www.gormanalysis.com/blog/connecting-to-aws-s3-with-python/).
- **MotherDuck** вместо локальной базы DuckDB, в том числе для запросов к данным в S3. Это облачное хранилище данных; в оригинале предлагается бесплатный вариант регистрации. Настройка описана в [документации](https://motherduck.com/docs/getting-started), а подключение S3 — в [отдельном руководстве](https://motherduck.com/docs/integrations/amazon-s3).

В начальном проекте уже есть логика переключения локальных и облачных хранилищ и путей. Переменная окружения `DAGSTER_ENVIRONMENT=prod` включает пути и ресурсы production.

Перед запуском в Dagster+ нужно:

1. Настроить бакет S3 для скачиваемых и создаваемых файлов ассетов.
2. Создать аккаунт MotherDuck для замены локальной базы DuckDB.
3. Настроить в MotherDuck доступ к бакету S3 с помощью учётных данных AWS с нужными правами.
4. Добавить целевое окружение production в проект dbt.
5. Добавить в Dagster+ переменные окружения с параметрами AWS и токеном MotherDuck.

Далее рассмотрим шаги 4 и 5.

---

## Целевое окружение production в profiles.yml

Добавим второе целевое окружение в профиль `dagster_dbt_university` файла `analytics/profiles.yml`. [Target в dbt](https://docs.getdbt.com/docs/core/connect-data-platform/connection-profiles#understanding-targets-in-profiles) описывает подключение к хранилищу данных. До сих пор это была локальная база DuckDB.

Чтобы разделить разработку и production, добавьте `prod`:

```yaml
dagster_dbt_university:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: '../../../{{ env_var("DUCKDB_DATABASE", "data/staging/data.duckdb") }}'
    prod:
      type: duckdb
      path: '{{ env_var("DUCKDB_DATABASE", "") }}'
```

MotherDuck использует DuckDB, поэтому тип подключения `prod` тоже будет `duckdb`. Сохраните файл и закоммитьте его.

**Примечание:** dbt поддерживает и другие платформы, но учебный проект рассчитан на DuckDB. Настройки другого `type` будут отличаться. Примеры — в [документации dbt](https://docs.getdbt.com/docs/supported-data-platforms).

---

## Целевое окружение prod в DbtProject

Обновим объект `DbtProject` в `src/dagster_and_dbt/defs/project.py`, чтобы выбирать target через переменную окружения.

1. В `.env` задайте `DBT_TARGET=dev`:

   ```python
   DBT_TARGET=dev
   ```

2. В начало `project.py` добавьте импорт `os`:

   ```python
   import os
   ```

3. При инициализации `DbtProject` задайте target из переменной окружения:

```python
dbt_project = DbtProject(
   project_dir=Path(__file__).joinpath("../..", "analytics").resolve(),
   target=os.getenv("DBT_TARGET")
)
```

---

## Целевое окружение prod в deploy.yml

В `.github/workflows/deploy.yml` укажите `DBT_TARGET=prod`, чтобы при подготовке проекта в GitHub Actions dbt использовал нужное подключение.

Найдите раздел переменных окружения (в оригинале примерно строка 12) и добавьте значение:

```bash
env:
  DAGSTER_CLOUD_URL: ${{ secrets.DAGSTER_CLOUD_ORGANIZATION }}
  DAGSTER_CLOUD_API_TOKEN: ${{ secrets.DAGSTER_CLOUD_API_TOKEN }}
  ENABLE_FAST_DEPLOYS: 'true'
  PYTHON_VERSION: '3.12'
  DAGSTER_CLOUD_FILE: 'dagster_cloud.yaml'
  DBT_TARGET: 'prod'
```

Сохраните файл, закоммитьте и отправьте изменения в удалённый репозиторий.

---

## Переменные окружения в Dagster+

При локальной работе переменные были доступны через `.env`. В новом окружении их нужно настроить заново.

### Необходимые переменные

{% table %}

- Переменная {% width="30%" %}
- Описание

---

- `DUCKDB_DATABASE`
- Строка подключения MotherDuck с сервисным токеном: `md:?motherduck_token=<insert_token_here>`. Подробнее — в [документации MotherDuck](https://motherduck.com/docs/authenticating-to-motherduck/#authentication-using-a-service-token).

---

- `DAGSTER_ENVIRONMENT`
- Установите `prod`. Используется ресурсами и константами проекта.

---

- `DBT_TARGET`
- Установите `prod`. Указывает проекту и ресурсу dbt, какое целевое окружение использовать.

---

- `AWS_ACCESS_KEY_ID`
- Идентификатор ключа доступа AWS с правами на нужный бакет S3.

---

- `AWS_SECRET_ACCESS_KEY`
- Секретный ключ доступа AWS, соответствующий этому идентификатору.

---

- `AWS_REGION`
- Регион, в котором находится бакет S3.

---

- `S3_BUCKET_PREFIX`
- URI бакета S3 для данных такси. Значение по умолчанию в примере — `"s3://dagster-university/"`; укажите свой бакет.

{% /table %}

### Создание переменных окружения

1. В интерфейсе Dagster+ откройте **Deployment > Environment variables**.
2. Нажмите **Add environment variable** справа.
3. В окне **Create environment variable** заполните:
    1. **Name** — имя переменной, например `DUCKDB_DATABASE`.
    2. **Value** — её значение.
    3. **Code location scope** — снимите **All code locations** и выберите только расположение кода учебного проекта.
4. Нажмите **Save**.

Повторите действия для всех переменных.

---

## Запуск пайплайна

Теперь пайплайн готов к выполнению в production. Откройте граф ассетов, нажмите **Materialize all** и наблюдайте за запуском.
