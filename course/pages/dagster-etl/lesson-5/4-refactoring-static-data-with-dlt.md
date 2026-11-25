---
title: 'Урок 5: Рефакторинг загрузки статических данных с dlt'
module: 'dagster_etl'
lesson: '5'
---

# Рефакторинг загрузки статических данных с dlt

Между исходным CSV-пайплайном и простым примером dlt, который мы только что преобразовали в ассеты Dagster, есть два ключевых отличия. Во-первых, CSV-пайплайн использует конфигурацию запуска для передачи конкретного имени файла во время выполнения. Во-вторых, ассет dlt в данном случае зависит от вышестоящего ассета, подготавливающего файл.

Начнём с повторного использования существующей конфигурации запуска и вышестоящего ассета. Оба можно оставить без изменений. Это позволит сохранить гибкий файловый интерфейс, заменив механизм загрузки данных на dlt:

```python
# src/dagster_and_etl/defs/assets.py
class FilePath(dg.Config):
    path: str


@dg.asset
def import_file(context: dg.AssetExecutionContext, config: FilePath) -> str:
    file_path = (
        Path(__file__).absolute().parent / f"../../../data/source/{config.path}"
    )
    return str(file_path.resolve())
```

Далее необходимо определить функцию `dlt.source` для CSV-пайплайна. Она будет очень похожа на ранее использованную функцию `simple_source`, но с несколькими изменениями: она читает CSV-файл и принимает путь к файлу как входной параметр. Это позволяет динамически передавать обрабатываемый файл, поручая dlt определение схемы:

```python {% obfuscated="true" %}
@dlt.source
def csv_source(file_path: str = None):
    def load_csv():
        import pandas as pd
        df = pd.read_csv(file_path)
        yield df.to_dict(orient="records")

    return load_csv
```

Здесь важно использовать `pandas.read_csv()`: в отличие от встроенного `csv.DictReader` Python, pandas определяет типы столбцов на основе данных, предоставляя dlt типизированные значения для записи корректной схемы в DuckDB.

Это очень полезно. Ранее приходилось жёстко задавать схему целевой таблицы в пайплайнах. Передача управления схемой фреймворку может существенно уменьшить количество ошибок. Однако всё равно следует понимать, какие типы данных он выбрал. Например, почтовый индекс может выглядеть как целое число, но это не означает, что его следует хранить как число.

Пока всё выглядит очень похоже на предыдущую настройку. Мы снова используем декоратор `@dlt_assets` для создания ассетов на основе dlt. Главное отличие — функция `csv_source` принимает входной параметр с путём к файлу.

Как и в предыдущем пайплайне Dagster, этот параметр будет предоставлен вышестоящим ассетом `import_file`. Это позволяет ассету dlt динамически получать путь к файлу и выполнять ETL для конкретного файла, возвращённого `import_file`:

```python {% obfuscated="true" %}
@dlt_assets(
    dlt_source=csv_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="csv_pipeline",
        dataset_name="csv_data",
        destination="duckdb",
        progress="log",
    ),
)
def dlt_csv_assets(
    context: dg.AssetExecutionContext, dlt: DagsterDltResource, import_file
):
    yield from dlt.run(context=context, dlt_source=csv_source(import_file))
```

## Транслятор dlt

Настройка выглядит завершённой, но остаётся ещё один шаг. Поскольку ассеты dlt создаются иначе, они также по-особому обрабатывают зависимости.

Если ты проходил [курс Dagster & dbt](https://courses.dagster.io/courses/dagster-dbt), возможно, помнишь необходимость использовать транслятор для сопоставления ассетов dbt с другими ассетами проекта Dagster. Для dlt мы аналогично используем специализированный транслятор (`DagsterDltTranslator`).

В данном случае нужно сопоставить ассет dlt с зависимостью от ассета import_file, чтобы путь к файлу, возвращаемый import_file, передавался функции источника dlt. Это довольно просто реализовать. Наш транслятор будет выглядеть так:

```python
class CustomDagsterDltTranslator(DagsterDltTranslator):
    def get_asset_spec(self, data: DltResourceTranslatorData) -> dg.AssetSpec:
        default_spec = super().get_asset_spec(data)
        return default_spec.replace_attributes(
            deps=[dg.AssetKey("import_file")],
        )
```

После определения транслятора можно передать его в декоратор `dlt_assets` через параметр `dagster_dlt_translator`:

```python
@dlt_assets(
    ...
    dagster_dlt_translator=CustomDagsterDltTranslator(),
)
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
