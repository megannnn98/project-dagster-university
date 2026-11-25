---
title: 'Урок 3: Сложные партиции'
module: 'dagster_etl'
lesson: '3'
---

# Сложные партиции

Партиции по времени обычно легко реализовать. Они следуют регулярным закономерностям (день, неделя, месяц) и имеют предсказуемые границы.

Но что делать, если поступающие данные не следуют фиксированному шаблону? Например, если данные сгруппированы по имени клиента? В таком случае набор партиций может меняться со временем по мере появления новых клиентов.

Как организовать партиции, чтобы отслеживать входные данные даже при нерегулярном поступлении?

## Динамические партиции

Помимо партиций по времени Dagster поддерживает динамические партиции. Они обеспечивают большую гибкость. В отличие от временных партиций, динамические позволяют точно управлять включаемыми значениями и расширять набор партиций по мере появления новых категорий данных (например, имён клиентов).

Создать динамическое определение партиций просто. Нужно только имя:

```python
dynamic_partitions_def = dg.DynamicPartitionsDefinition(name="dynamic_partition")
```

Так определяется набор динамических партиций с именем "dynamic_partition", в который можно добавить любые необходимые партиции.

## Ассеты с динамическими партициями

По аналогии с временными партициями создадим новый набор ассетов. Логика ассета вновь остаётся прежней, но используется динамическое определение партиций:

```python {% obfuscated="true" %}
# src/dagster_and_etl/defs/assets.py
@dg.asset(
    partitions_def=dynamic_partitions_def,
)
def import_dynamic_partition_file(context: dg.AssetExecutionContext) -> str:
    file_path = (
        Path(__file__).absolute().parent
        / f"../../../data/source/{context.partition_key}.csv"
    )
    return str(file_path.resolve())
```

Если теперь попробовать выполнить этот ассет в Dagster, окажется, что его нельзя материализовать. Причина в том, что в `dynamic_partitions_def` ещё не добавлены партиции. Это ожидаемо: по умолчанию динамические партиции пусты и не имеют встроенной логики определения допустимых ключей. Мы сами регистрируем значения партиций, которые хотим выполнить.

Перед запуском пайплайна определим нижестоящий ассет, загружающий данные в DuckDB с использованием значений динамических партиций:

```python {% obfuscated="true" %}
# src/dagster_and_etl/defs/assets.py
@dg.asset(
    kinds={"duckdb"},
    partitions_def=dynamic_partitions_def,
)
def duckdb_dynamic_partition_table(
    context: dg.AssetExecutionContext,
    database: DuckDBResource,
    import_dynamic_partition_file,
):
    table_name = "raw_dynamic_partition_data"
    with database.get_connection() as conn:
        table_query = f"""
            create table if not exists {table_name} (
                date date,
                share_price float,
                amount float,
                spend float,
                shift float,
                spread float
            ) 
        """
        conn.execute(table_query)
        conn.execute(
            f"delete from {table_name} where date = ?;", [context.partition_key]
        )
        conn.execute(f"copy {table_name} from ?;", [import_dynamic_partition_file])
```

Эта настройка очень похожа на ранее созданные дневные партиции. Но как это работает на практике? Для понимания различий рассмотрим способы запуска партиционированных пайплайнов. Каждый тип требует своего подхода к расписаниям и оркестрации в зависимости от того, как и когда появляются новые данные.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
