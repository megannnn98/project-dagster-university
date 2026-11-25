---
title: "Урок 4: Настройка выполнения"
module: 'dagster_dbt'
lesson: '4'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Настройка выполнения

На странице модели dbt в каталоге ассетов можно увидеть исходный код dbt. Он помогает понять запрос, но не показывает окончательный SQL после обработки шаблонов Jinja. Описание ассета формируется при _загрузке_ расположения кода, а модель компилируется и выполняется позже, _во время запуска_.

Изменим тело определения `@dbt_assets`, чтобы получать артефакт `run_results.json` завершённого запуска и выводить скомпилированный SQL каждой модели. Это также покажет, как добавлять собственную логику выполнения.

В `defs/assets/dbt.py`:

1. Сейчас `yield from` сразу передаёт события из генератора `.stream()`. После потребления генератор исчерпан. Чтобы затем обращаться к артефактам через `.get_artifact()`, сохраним сам объект вызова `dbt.cli()` в переменной `dbt_build_invocation`:

   ```python
    dbt_build_invocation = dbt.cli(["build"], context=context)
   ```

2. Передадим события из `dbt_build_invocation.stream()` с помощью `yield from`, сохранив прежнюю передачу событий команды dbt:

   ```python
   dbt_build_invocation = dbt.cli(["build"], context=context)

   yield from dbt_build_invocation.stream()
   ```

3. Через сохранённый объект вызова получим `run_results.json` методом `get_artifact`. Этот артефакт содержит результаты отдельных узлов, сведения о времени выполнения и, для соответствующих результатов, скомпилированный SQL:

   ```python
   dbt_build_invocation = dbt.cli(["build"], context=context)

   yield from dbt_build_invocation.stream()

   run_results_json = dbt_build_invocation.get_artifact("run_results.json")
   ```

4. Переберём результаты и запишем SQL в журнал с уровнем `DEBUG`, используя логгер из `context`:

   ```python
   dbt_build_invocation = dbt.cli(["build"], context=context)

   yield from dbt_build_invocation.stream()

   run_results_json = dbt_build_invocation.get_artifact("run_results.json")
   for result in run_results_json["results"]:
       context.log.debug(result["compiled_code"])
   ```

Перезагрузите расположение кода и запустите модели dbt. В журнале должен появиться их скомпилированный SQL. Пример предполагает наличие `compiled_code` в каждой обрабатываемой записи; если среди результатов есть другие типы узлов без этого поля, добавьте проверку перед обращением к нему.

В определении `@dbt_assets` можно выполнять и другую логику, например отправлять метаданные запусков dbt во внешние сервисы.
