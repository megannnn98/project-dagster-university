---
title: 'Урок 5: Интеграционные тесты'
module: 'dagster_testing'
lesson: '5'
---

# Интеграционные тесты

Начнём с определения нового ассета, аналогичного `state_population_file`, который получает данные о населении городов из базы данных.

Предположим, что в нашем рабочем хранилище данных существует таблица `data.city_population`, содержащая все города всех штатов. Таблица имеет следующую схему.

| Имя | Тип | Описание |
| --- | --- | --- |
| state_name | VARCHAR(100) | Название штата |
| city_name | VARCHAR(100) | Название города |
| population | INT | Население города |

В коде ассета явно укажем поиск городов штата Нью-Йорк и будем возвращать результаты запроса к Snowflake с помощью ресурса.

```python
@dg.asset
def state_population_database(database: SnowflakeResource) -> list[tuple]:
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

При запуске этого ассета необходимо передать ресурс Snowflake. Подключение к Snowflake определяется переменными окружения при инициализации ресурса и задаётся в Definitions для ресурсов.

```python
@dg.definitions
def resources():
    return dg.Definitions(
        resources={
            "database": snowflake_resource,
        },
    )
```

Это хороший способ структурирования кода. Мы отделяем код приложения от конфигурации в соответствии с методологией [Twelve-Factor](https://12factor.net/).

Это означает, что можно написать интеграционный тест, использующий Snowflake, но с другой конфигурацией для подключения к другой базе данных. Например, в нашей учётной записи Snowflake может существовать отдельная staging-база.

```python
def test_snowflake_staging():
    snowflake_staging_resource = SnowflakeResource(
        account=dg.EnvVar("SNOWFLAKE_ACCOUNT"),
        user=dg.EnvVar("SNOWFLAKE_USERNAME"),
        password=dg.EnvVar("SNOWFLAKE_PASSWORD"),
        database="STAGING",
        warehouse="STAGING_WAREHOUSE",
    )

    lesson_5.state_population_database(snowflake_staging_resource)
```

Это интеграционный тест: мы выполняем ассет и проверяем, что он работает с настоящим подключением к Snowflake. Это хороший шаг, но такой подход не всегда подходит для тестирования.

У подобных интеграционных тестов есть несколько недостатков. Поскольку Snowflake использует оплату по потреблению, каждый запуск теста будет стоить денег. Кроме того, при запросах к облачной OLAP-системе нет гарантий относительно времени выполнения теста: он может занять одну-две секунды или целую минуту в зависимости от выделенных вычислительных ресурсов. Наконец, предполагается наличие эквивалентного staging-окружения в Snowflake. Возможно, у нас нет staging-базы с подходящими для тестирования данными.

Один из способов избежать этих проблем — поддерживать отдельное окружение специально для интеграционных тестов. Тогда потребуется подставить это подключение в наш ассет. Именно здесь Dagster помогает реализовывать интересные сценарии интеграционного тестирования.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
