---
title: 'Урок 9: Создание сенсора'
module: 'dagster_essentials'
lesson: '9'
---

# Создание сенсора

Теперь, когда новый актив и конфигурация настроены, создадим сенсор, реагирующий на события материализацией актива `adhoc_request`.

В общих чертах мы будем отслеживать появление новых запросов в виде JSON-файлов в каталоге `data/requests`, предполагать, что файл содержит корректные значения, и инициировать запуск `adhoc_request_job`, используя значения запроса в качестве конфигурации. Конфигурация этого запуска будет доступна активу `adhoc_request` во время материализации.

---

## Курсоры сенсоров

Прежде чем приступить к созданию сенсора, поговорим о его **курсоре (cursor)**.

Курсор — сохранённое значение, используемое для управления состоянием сенсора. Создаваемый сенсор использует курсор, чтобы отслеживать запросы, для которых уже сформированы отчёты. Другие примеры использования курсора — хранение идентификатора последней полученной записи или позиции, на которой закончилось предыдущее вычисление.

Сенсор будет получать все имена файлов в каталоге `data/requests`, сравнивать их со списком уже просмотренных файлов, сохранённым в курсоре, обновлять курсор новыми файлами и инициировать новый запуск для каждого файла.

Большинство сенсоров имеют похожий жизненный цикл:

1. Прочитать курсор.
2. Сделать новое наблюдение и сравнить его с курсором.
3. Если есть изменения, инициировать запуск для каждого нового изменения.
4. Обновить курсор с учётом изменений.

---

## Написание сенсора

Разобравшись с курсорами, приступим к написанию сенсора.

1. Создай каркас файла сенсора:

    ```bash
    dg scaffold defs dagster.sensor sensors.py
    ```

2. Проверь, что всё настроено правильно:

    ```bash
    dg check defs
    ```

3. Добавь следующие импорты в начало файла:

   ```python
   # src/dagster_essentials/defs/sensors.py
   import dagster as dg
   import os
   import json

   from dagster_essentials.defs.jobs import adhoc_request_job
   ```

   Разберём эти импорты:

   - Стандартная библиотека `os` будет использоваться для просмотра файлов в каталоге `data/requests`.
   - Стандартная библиотека `json` будет использоваться для чтения JSON-файлов запросов по мере необходимости.
   - `adhoc_request_job` указывает, что сенсор будет инициировать запуски этого задания.

4. Для определения сенсора создай новую функцию, принимающую параметр `context`. Подобно аргументу контекста активов типа `AssetExecutionContext`, определения сенсоров используют `SensorEvaluationContext` для получения информации и метаданных о текущем вычислении сенсора. Код должен выглядеть так:

   ```python
   import dagster as dg

   @dg.sensor
   def adhoc_request_sensor(context: dg.SensorEvaluationContext):
   ```

5. Добавь к функции декоратор `@dg.sensor` и передай `adhoc_request_job` в параметр job. Сейчас код должен выглядеть следующим образом:

   ```python
   @dg.sensor(
       job=adhoc_request_job
   )
   def adhoc_request_sensor(context: dg.SensorEvaluationContext):
   ```

6. Заполним тело функции. Создай переменную, указывающую на каталог `data/requests`, за которым будет наблюдать сенсор:

   ```python
   @dg.sensor(
       job=adhoc_request_job
   )
   def adhoc_request_sensor(context: dg.SensorEvaluationContext):
       PATH_TO_REQUESTS = os.path.join(
       os.path.dirname(__file__),
        "../../../",
       "data/requests",
   )
   ```

7. Определи курсор. Скопируй следующий код в тело функции сенсора:

   ```python
   previous_state = json.loads(context.cursor) if context.cursor else {}
   current_state = {}
   ```

   Разберём, что делает этот код. Аргумент `context` содержит курсор для управления состоянием уже просмотренных сенсором файлов. Курсор может существовать или отсутствовать в зависимости от того, происходили ли ранее тики сенсора.

   Поэтому проверяем наличие `context.cursor` и, если он существует, декодируем его строковое значение из JSON. Кроме того, инициализируем `current_state` пустым объектом, которым заменим курсор после просмотра каталога.

8. Далее инициализируй пустой список `runs_to_request`. В нём будут храниться новые запросы на запуск:

   ```python
   runs_to_request = []
   ```

9. Скопируй следующий код в сенсор, после чего разберём его:

   ```python
   for filename in os.listdir(PATH_TO_REQUESTS):
       file_path = os.path.join(PATH_TO_REQUESTS, filename)
       if filename.endswith(".json") and os.path.isfile(file_path):
           last_modified = os.path.getmtime(file_path)

           current_state[filename] = last_modified

           # if the file is new or has been modified since the last run, add it to the request queue
           if filename not in previous_state or previous_state[filename] != last_modified:
               with open(file_path, "r") as f:
                   request_config = json.load(f)

                   runs_to_request.append(dg.RunRequest(
                       run_key=f"adhoc_request_{filename}_{last_modified}",
                       run_config={
                           "ops": {
                               "adhoc_request": {
                                   "config": {
                                       "filename": filename,
                                       **request_config
                                   }
                               }
                           }
                       }
                   ))
   ```

   **Примечание:** при вставке в сенсор проверь корректность отступов, иначе возникнет ошибка Python.

   Этот пример:

   - Использует `os.listdir` для обхода каталога `data/requests`, проверяет каждый JSON-файл и выясняет по `previous_state`, обновился ли он или был ли ранее просмотрен.
   - Создаёт `RunRequest` для файла, если он обновился или отчёт по нему ещё не запускался.
   - Формирует уникальный `run_key`, включающий имя файла и время его последнего изменения.
   - Передаёт ключ запуска и конфигурацию в `RunRequest`. Через аргумент `run_config` и ключ `adhoc_request` указывается конфигурация, которую должен использовать актив `adhoc_request`.

10. Сенсоры ожидают возвращаемый объект `SensorResult`, содержащий всю необходимую информацию, например какие запуски инициировать и каким должен быть новый курсор. Добавь следующий код в конец функции сенсора:

   ```python
   return dg.SensorResult(
       run_requests=runs_to_request,
       cursor=json.dumps(current_state),
   )
   ```

Объединив всё вместе, ты должен получить следующий код в файле `sensors.py`:

```python
# src/dagster_essentials/defs/sensors.py
import dagster as dg
import os
import json

from dagster_essentials.defs.jobs import adhoc_request_job

@dg.sensor(
    job=adhoc_request_job
)
def adhoc_request_sensor(context: dg.SensorEvaluationContext) -> dg.SensorResult:
    PATH_TO_REQUESTS = os.path.join(
        os.path.dirname(__file__),
        "../../../",
        "data/requests",
    )
    previous_state = json.loads(context.cursor) if context.cursor else {}
    current_state = {}
    runs_to_request = []

    for filename in os.listdir(PATH_TO_REQUESTS):
        file_path = os.path.join(PATH_TO_REQUESTS, filename)
        if filename.endswith(".json") and os.path.isfile(file_path):
            last_modified = os.path.getmtime(file_path)

            current_state[filename] = last_modified

            # if the file is new or has been modified since the last run, add it to the request queue
            if filename not in previous_state or previous_state[filename] != last_modified:
                with open(file_path, "r") as f:
                    request_config = json.load(f)

                    runs_to_request.append(dg.RunRequest(
                        run_key=f"adhoc_request_{filename}_{last_modified}",
                        run_config={
                            "ops": {
                                "adhoc_request": {
                                    "config": {
                                        "filename": filename,
                                        **request_config
                                    }
                                }
                            }
                        }
                    ))

    return dg.SensorResult(
        run_requests=runs_to_request,
        cursor=json.dumps(current_state),
    )
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
