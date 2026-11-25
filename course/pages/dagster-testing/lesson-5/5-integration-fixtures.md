---
title: 'Урок 5: Фикстуры интеграционных тестов'
module: 'dagster_testing'
lesson: '5'
---

# Фикстуры интеграционных тестов

Поскольку для интеграционного теста Postgres всегда требуется Docker, можно создать фикстуру pytest, управляющую Docker. Возьмём использованные ранее команды CLI и обернём их в фикстуру.

```python
# tests/fixtures.py
@pytest.fixture(scope="session", autouse=True)
def docker_compose():
    file_path = Path(__file__).absolute().parent / "docker-compose.yaml"

    # Tear down any existing containers and volumes to ensure clean state
    subprocess.run(
        ["docker", "compose", "-f", file_path, "down", "-v"],
        capture_output=True,
    )

    # Start Docker Compose
    subprocess.run(
        ["docker", "compose", "-f", file_path, "up", "--build", "-d"],
        check=True,
        capture_output=True,
    )

    # Wait for PostgreSQL to be ready to accept connections
    max_retries = 10
    for i in range(max_retries):
        result = subprocess.run(
            ["docker", "exec", "postgresql", "pg_isready"],
            capture_output=True,
        )
        if result.returncode == 0:
            break
        time.sleep(2)

    # Wait for the initialization scripts to complete (schema and table creation)
    for i in range(max_retries):
        result = subprocess.run(
            [
                "docker",
                "exec",
                "postgresql",
                "psql",
                "-U",
                "test_user",
                "-d",
                "test_db",
                "-c",
                "SELECT 1 FROM data.city_population LIMIT 1;",
            ],
            capture_output=True,
        )
        if result.returncode == 0:
            break
        time.sleep(2)

    yield

    # Tear down Docker Compose and remove volumes
    subprocess.run(["docker", "compose", "-f", file_path, "down", "-v"], check=True)
```

Приведённый код:

1. Получает путь к файлу `docker-compose.yaml` относительно теста (он находится в том же каталоге).
2. Запускает сервис Docker с помощью команды `docker compose`.
3. Ожидает готовности сервиса, проверяя доступность базы с помощью `pg_isready`.
4. Передаёт управление тесту для его выполнения.
5. Останавливает сервис Docker после завершения тестирования.

Теперь эту фикстуру можно передать в параметры интеграционного теста, связав тест с необходимыми ему сервисами:

```python
# tests/test_lesson_5.py
def test_state_population_database(docker_compose):  # noqa: F811
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

```bash
> pytest tests/test_lesson_5.py::test_state_population_database
...
tests/test_lesson_5.py .                                                          [100%]
```

Поскольку область действия фикстуры pytest — сессия, она остаётся активной на протяжении выполнения всех использующих её тестов. Это полезно, поскольку интеграционные тесты выполняются дольше модульных. Большая часть времени уходит на запуск необходимых сервисов, а сами тесты выполняются относительно быстро.

Область действия на уровне сессии позволяет не запускать и не останавливать сервисы заново для каждого теста.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
