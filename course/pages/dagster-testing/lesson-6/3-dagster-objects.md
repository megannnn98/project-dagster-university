---
title: 'Урок 6: Тестирование других объектов Dagster'
module: 'dagster_testing'
lesson: '6'
---

# Тестирование других объектов Dagster

Большинство тестов будет связано с ассетами, поскольку в них сосредоточена основная логика обработки данных организации. Помимо теста Definitions, не стоит уделять столько же внимания тестированию остальных объектов Dagster. Однако вот несколько рекомендаций, если нужно протестировать их более подробно.

## Задания

Задания представляют собой набор ассетов, сгруппированных определённым образом. Обычно они используются для выполнения подмножества графа ассетов заранее заданным способом.

Вот два задания, использующие одно и то же подмножество графа ассетов, хотя `my_job_configured` также передаёт конфигурацию запуска.

```python
# src/dagster_testing/defs/jobs.py
my_job = dg.define_asset_job(
    name="jobs",
    selection=[
        dagster_assets.population_file_config,
        dagster_assets.population_api_resource,
        dagster_assets.population_combined,
    ],
)


my_job_configured = dg.define_asset_job(
    name="jobs_config",
    selection=[
        dagster_assets.population_file_config,
        dagster_assets.population_api_resource,
        dagster_assets.population_combined,
    ],
    config=yaml.safe_load(
        (Path(__file__).absolute().parent / "configs/run_config.yaml").open()
    ),
)
```

Если подумать, какие аспекты задания нужно проверить, большинство из них относятся к заданным нами параметрам, например выборке ассетов или конфигурации. Нет необходимости писать тесты, проверяющие сам механизм выполнения заданий: это ответственность Dagster.

Для тестирования заданий можно писать тесты их конфигураций, обращаясь к элементам объекта. Например, `my_job_configured` настраивается через YAML, и мы можем захотеть убедиться, что ассет всегда использует определённый путь к файлу.

```python
# tests/test_lesson_6.py
def test_job_config():
    assert (
        jobs.my_job_configured.config["ops"]["population_file_config"]["config"]["path"]
        == "tests/data/test.csv"
    )
```

```bash
> pytest tests/test_lesson_6.py::test_job_config
...
tests/test_lesson_6.py .                                                          [100%]
```

Подобные тесты нужны не всегда, но могут быть полезны в проектах Dagster, где необходимо гарантировать корректность всех аспектов конфигурации.

## Расписания

Как и задания, расписания позволяют обращаться к внутренним свойствам объекта. Рассмотрим следующее расписание.

```python
# src/dagster_testing/defs/schedules.py
my_schedule = dg.ScheduleDefinition(
    name="my_schedule",
    job=jobs.my_job,
    cron_schedule="0 0 5 * *",  # every 5th of the month at midnight
    run_config=dg.RunConfig(
        {
            "state_population_file_config": assets.FilepathConfig(
                path="tests/data/test.csv"
            )
        }
    ),
)
```

Можно написать тесты, проверяющие, что расписание срабатывает в нужное время и использует правильное задание. Проверка только значения строки cron подтверждает лишь введённую строку. Если ожидаемое значение скопировано из той же ошибочной конфигурации, такая проверка не обнаружит запуск в неправильный день. Использование `croniter` для вычисления фактического времени срабатывания помогает выявить этот класс ошибок.

```python
# tests/test_lesson_6.py
from croniter import croniter
from datetime import datetime

def test_schedule():
    assert schedules.my_schedule
    assert schedules.my_schedule.job == jobs.my_job

    cron = schedules.my_schedule.cron_schedule
    # From Jan 1, the first trigger should be Jan 5 at midnight
    base = datetime(2024, 1, 1, 0, 0)
    it = croniter(cron, base)
    assert it.get_next(datetime) == datetime(2024, 1, 5, 0, 0)
    # The run after that should be Feb 5 at midnight
    assert it.get_next(datetime) == datetime(2024, 2, 5, 0, 0)
```

```bash
> pytest tests/test_lesson_6.py::test_schedule
...
tests/test_lesson_6.py .                                                          [100%]
```

Если выражение cron случайно записать как `"0 0 6 * *"` (шестое число вместо пятого), `croniter` вычислит время срабатывания `datetime(2024, 1, 6, 0, 0)`, и проверка завершится ошибкой.

## Сенсоры

Пользовательские сенсоры — один из объектов Dagster, для которых может быть полезно написать отдельные тесты. В отличие от заданий и расписаний, сенсоры допускают гораздо больше настроек и пользовательской логики, поэтому может потребоваться убедиться, что они срабатывают ожидаемым образом.

В нашем примере есть простой сенсор, проверяющий наличие новых файлов (для целей урока он делает это на основе `random.random()`) и в зависимости от результата запрашивающий запуск или пропускающий выполнение.

```python
# src/dagster_testing/defs/sensors.py
def check_for_new_files() -> list[str]:
    if random.random() > 0.5:
        return ["file1", "file2"]
    return []


@dg.sensor(
    name="my_sensor",
    job=jobs.my_job_configured,
    minimum_interval_seconds=5,
)
def my_sensor():
    new_files = check_for_new_files()
    # New files, run `my_job`
    if new_files:
        for filename in new_files:
            yield dg.RunRequest(run_key=filename)
    # No new files, skip the run and log the reason
    else:
        yield dg.SkipReason("No new files found")
```

Хороший тест этого сенсора должен проверять, что он действительно срабатывает при появлении нового файла и не запускает задание, если новых файлов нет. Для этого нужно определить основную логику срабатывания. В данном случае это возврат новых файлов функцией `check_for_new_files`.

Чтобы написать надёжный тест сенсора, вернёмся к уроку о mock-объектах. Подменим функцию `check_for_new_files` и зададим её возвращаемое значение, чтобы проверить оба случая — появление и отсутствие новых файлов.

Сначала напишем тест, в котором сенсор пропускает запуск.

```python
# tests/test_lesson_6.py
@patch("dagster_testing.defs.sensors.check_for_new_files", return_value=[])
def test_sensor_skip(mock_check_new_files):
    instance = dg.DagsterInstance.ephemeral()
    context = dg.build_sensor_context(instance=instance)
    assert sensors.my_sensor(context).__next__() == dg.SkipReason("No new files found")
```

```bash
> pytest tests/test_lesson_6.py::test_sensor_skip
...
tests/test_lesson_6.py .                                                          [100%]
```

Приведённый код:

1. Подменяет `check_for_new_files` и задаёт возвращаемое значение в виде пустого списка.
2. Инициализирует временный экземпляр Dagster, необходимый при тестировании аспектов Dagster, использующих демон.
3. Создаёт контекст сенсора с этим экземпляром.
4. Выполняет сенсор. Он возвращает генератор, из которого мы получаем первый элемент через `__next__()` и проверяем его соответствие `SkipReason`.

Как будет выглядеть тест, проверяющий обнаружение сенсором нового файла? Нажми **View answer**, чтобы посмотреть ответ.

```python {% obfuscated="true" %}
# tests/test_lesson_6.py
@patch(
    "dagster_testing.defs.sensors.check_for_new_files",
    return_value=["test_file"],
)
def test_sensor_run(mock_check_new_files):
    instance = dg.DagsterInstance.ephemeral()
    context = dg.build_sensor_context(instance=instance)
    assert sensors.my_sensor(context).__next__() == dg.RunRequest(run_key="test_file")
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
