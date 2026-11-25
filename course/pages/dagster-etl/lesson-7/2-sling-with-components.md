---
title: 'Урок 7: Sling с компонентами'
module: 'dagster_etl'
lesson: '7'
---

# Sling с компонентами

Для работы с компонентами Dagster будем использовать командную строку `dg`. Это полезный инструмент для инициализации проектов Dagster и навигации по ним. Поскольку мы работали в готовом виртуальном окружении и структуре проекта курса, до сих пор нам нечасто требовался `dg`.

Ранее мы использовали `dg` для запуска интерфейса, просмотра и выполнения ассетов, а теперь воспользуемся им для создания заготовки компонента.

## Создание компонента Sling

Для инициализации компонента Sling выполним команду `dg`, создающую заготовку компонента `dagster_sling.SlingReplicationCollectionComponent`:

```bash
dg scaffold defs 'dagster_sling.SlingReplicationCollectionComponent' ingest_files
```

Теперь в `defs` появится новый каталог с двумя файлами:

```
.
└── src
    └── dagster_and_etl
        └── defs
            └── ingest_files
                ├── defs.yaml
                └── replication.yaml
```

Это единственные два файла, с которыми нам нужно работать для настройки ассетов Sling (без Python). Рассмотрим содержимое каждого.

## Настройка YAML

Файл `replication.yaml` должен быть знаком. Это YAML-файл, определяющий параметры репликации Sling. Файл `replication.yaml`, сгенерированный командой `dg`, практически пуст:

```yaml
source: {}
streams: {}
target: {}
```

Скопируем в него всё содержимое файла `sling_replication.yaml` из предыдущего урока:

```yaml
source: MY_POSTGRES
target: MY_DUCKDB

defaults:
  mode: full-refresh

  object: "{stream_schema}_{stream_table}"

streams:
  data.customers:
  data.products:
  data.orders:
    mode: incremental
    primary_key: order_id
    update_key: order_date
```

Следующий файл — `defs.yaml`. Он содержит две части информации: какой компонент используется (в данном случае Sling) и расположение файла `replication.yaml`.

```
type: dagster_sling.SlingReplicationCollectionComponent

attributes:
  replications:
    - path: replication.yaml
```

Нам осталось добавить параметры подключения. Раньше мы определяли их в `SlingResource`, но при использовании компонентов это не требуется. Вместо этого укажем параметры подключения в YAML-файле определения компонента:

```yaml
type: dagster_sling.SlingReplicationCollectionComponent

attributes:
  sling:
    connections:
      - name: MY_POSTGRES
        type: postgres
        host: localhost
        port: 5432
        database: test_db
        user: test_user
        password: test_pass
      - name: MY_DUCKDB
        type: duckdb
        instance: duckdb:///var/tmp/duckdb.db
  replications:
    - path: replication.yaml
```

Обрати внимание: имена подключений в `defs.yaml` по-прежнему должны соответствовать именам в `replication.yaml` (`MY_DUCKDB` и `MY_POSTGRES`).

![Сравнение компонента и ассетов Sling](/images/dagster-etl/extra-credit/components-vs-asset.png.png)

## Просмотр ассетов

Поскольку мы перевели ассеты на компоненты, можно удалить значительную часть кода Python. Из `resources.py` можно удалить всё, что связано со Sling, а из файла `assets.py` — ассеты, созданные с помощью `sling_assets`. Ассеты, зависящие от ассетов компонента, можно оставить.

Теперь, если выполнить `dg dev`, мы увидим тот же граф ассетов, что и раньше.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
