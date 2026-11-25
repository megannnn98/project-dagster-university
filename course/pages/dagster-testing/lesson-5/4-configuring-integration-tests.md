---
title: 'Урок 5: Настройка интеграционных тестов'
module: 'dagster_testing'
lesson: '5'
---

# Настройка интеграционных тестов

Как уже упоминалось, Postgres — база данных с открытым исходным кодом и общедоступным дистрибутивом. В том числе существует образ [Docker](https://www.docker.com/), который можно использовать для тестирования.

Docker — платформа с открытым исходным кодом, позволяющая разработчикам запускать приложения в легковесных переносимых контейнерах. Это удобный способ запускать временные экземпляры сервисов, необходимых для тестов.

## Конфигурация Docker

{% callout %}

> 💡 **Docker:** мы не будем подробно изучать Docker. Главное — понять, как он помогает создавать более сложные интеграционные тесты.

> {% /callout %}

Для настройки Docker сначала определим, что нам необходимо:

1. Сервис с работающим Postgres.
2. Таблица `data.city_population`, заполненная тестовыми записями для запросов.

Начнём с создания файла `docker-compose.yml`. Он определяет все сервисы Docker, необходимые для интеграционного теста. В данном случае это только база Postgres:

```yaml
---

services:
  postgresql:
    build:
      context: ./postgres
    container_name: postgresql
    environment:
      POSTGRES_DB: "test_db"
      POSTGRES_USER: "test_user"
      POSTGRES_PASSWORD: "test_pass"
    ports:
      - "5432:5432"
```

Если ты знаком с Docker, то заметишь, что мы указываем каталог контекста сборки, а не готовый образ. Этот каталог содержит Dockerfile с образом Postgres и файлом инициализации.

```yaml
FROM postgres:17-alpine

COPY postgres_bootstrap.sql /docker-entrypoint-initdb.d/
```

Такая сборка использует образ `postgres:17-alpine` и копирует файл `postgres_bootstrap.sql`, который будет выполнен при первоначальной инициализации базы. SQL-файл создаёт схему, таблицу и добавляет несколько тестовых записей.

```sql
CREATE SCHEMA data;

CREATE TABLE data.city_population (
    state_name VARCHAR(100),
    city_name VARCHAR(100),
    population INT
);

INSERT INTO data.city_population VALUES
('NY', 'New York', 8804190),
('NY', 'Buffalo', 278349),
('CA', 'Los Angeles', 3898747);
```

## Запуск Docker

Это вся необходимая конфигурация Docker. Теперь можно запустить базу Postgres через CLI Docker:

```bash 
> docker compose -f tests/docker-compose.yaml up -d
[+] Running 2/2
 ✔ Network tests_default  Created                                                   0.0s
 ✔ Container postgresql                   Started                                                   0.2s
```

Флаг `-d` запускает сервис в фоновом режиме. При первом запуске может понадобиться больше времени, поскольку необходимо загрузить образ Postgres и инициализировать базу. Последующие запуски будут быстрее.

Если нужно остановить сервис Docker, выполни:

```bash
docker compose -f tests/docker-compose.yaml down
```

## Запуск тестов с Docker

Когда Postgres запущен в Docker, можно определить тест, инициализирующий ресурс `PostgresResource`.

```python
# tests/test_lesson_5.py
def test_state_population_database():
    postgres_resource = PostgresResource(
        host="localhost",
        user="test_user",
        password="test_pass",
        database="test_db",
    )

    result = lesson_5.state_population_database(postgres_resource)
    assert result == [
        ("New York", 8804190),
        ("Buffalo", 278349),
    ]
```

Можно увидеть, как все части тестового кода работают вместе.

![Тест с Docker](/images/dagster-testing/lesson-5/docker-test.png)

1. `postgres_resource` инициализируется с параметрами подключения сервиса Docker Compose.
2. База Postgres возвращает данные, заданные в SQL-скрипте.

Убедимся, что всё работает, с помощью pytest.

```bash
> pytest tests/test_lesson_5.py::test_state_population_database
...
tests/test_lesson_5.py .                                                          [100%]
```

## Тестирование с materialize

Как и при тестировании с ресурсами, можно использовать `dg.materialize()` в интеграционных тестах для проверки нескольких ассетов.

```python
# tests/test_lesson_5.py
@pytest.mark.integration
def test_assets(docker_compose, postgres_resource, query_output_ny):  # noqa: F811
    result = dg.materialize(
        assets=[
            lesson_5.state_population_database,
            lesson_5.total_population_database,
        ],
        resources={"database": postgres_resource},
    )
    assert result.success

    assert result.output_for_node("state_population_database") == query_output_ny
    assert result.output_for_node("total_population_database") == 9082539
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
