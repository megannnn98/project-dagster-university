---
title: 'Урок 5: Ресурсы для интеграционных тестов'
module: 'dagster_testing'
lesson: '5'
---

# Ресурсы для интеграционных тестов

Рассмотрим ассет `state_population_database`. Мы хотим убедиться, что он способен выполнить запрос и вернуть результат, но не обязательно должны использовать конкретную базу данных. Вместо требования, чтобы ресурс `database` был именно Snowflake, можно изменить аннотацию, позволяя принимать произвольный ресурс:

```python
# src/dagster_testing/defs/assets/lesson_5.py
@dg.asset
def state_population_database(database: dg.ConfigurableResource) -> list[tuple]:
    query = """
        SELECT
            city_name,
            population
        FROM data.city_population
        WHERE state_name = 'NY';
    """
    with database.get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        return cur.fetchall()
```

Теперь для выполнения ассета достаточно предоставить ресурс с контекстным менеджером `get_connection` и методами `cursor` и `execute`. С точки зрения Dagster это может быть любой объект, даже не обязательно база данных, если он удовлетворяет этим требованиям.

Для наших целей создадим ресурс с похожей функциональностью, но использующий другую базу данных. Возьмём Postgres, который, в отличие от Snowflake, имеет открытый исходный код и может бесплатно запускаться локально.

Ещё одно преимущество Postgres — его клиент Python во многом похож на клиент Snowflake. Вот ресурс, позволяющий выполнять запросы в Postgres. Нажми **View answer**, чтобы посмотреть ответ.

```python {% obfuscated="true" %}
# tests/test_lesson_5.py
class PostgresResource(dg.ConfigurableResource):
    user: str
    password: str
    host: str
    database: str

    def _connection(self):
        return psycopg2.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database,
        )

    @contextmanager
    def get_connection(self):
        yield self._connection()
```

Этот ресурс предоставляет всё необходимое и может использоваться вместо ресурса Snowflake при интеграционном тестировании, чтобы проверить работу ассета с подключением к базе данных.

{% callout %}

> 💡 **Синтаксис SQL:** при использовании другой базы данных для интеграционного тестирования нужно учитывать различия синтаксиса SQL. Snowflake и Postgres поддерживают большую часть общего [стандартного SQL](https://docs.snowflake.com/en/guides-overview-queries), но Snowflake также содержит синтаксические конструкции и функции, отсутствующие в Postgres.

> {% /callout %}

## Аналогичные ресурсы

Мы определили собственный ресурс Postgres вместо Snowflake, но есть и другие варианты. Один из популярных инструментов — DuckDB, локальная OLAP-база данных. Она может стать хорошей заменой хранилищу данных вроде Snowflake. Однако следует учитывать различия между Python-клиентами Snowflake и DuckDB. Например, такой код:

```python
@dg.asset
def truncate_table(database: dg.ConfigurableResource) -> None:
    query = "TRUNCATE TABLE data.city_population"
    with database.get_connection() as conn:
        conn.execute(query)
```

Не будет работать со Snowflake, поскольку Snowflake требует `cursor`, а DuckDB — нет. Код должен подходить для обоих ресурсов:

```python
@dg.asset
def truncate_table(database: dg.ConfigurableResource) -> None:
    query = "TRUNCATE TABLE data.city_population"
    with database.get_connection() as conn:
        cur = conn.cursor() # Cursor is required
        cur.execute(query)
```

Ресурс DuckDB может лучше соответствовать твоим задачам, но для демонстрации мы используем собственный ресурс Postgres.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
