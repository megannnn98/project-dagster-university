---
title: "Урок 7: Создание манифеста при развёртывании"
module: 'dbt_dagster'
lesson: '7'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Создание манифеста при развёртывании

На предыдущем шаге Dagster не нашёл манифест, необходимый для представления моделей dbt как ассетов. При локальной разработке мы создавали его через `dbt parse` в третьем уроке, затем автоматизировали подготовку методом `DbtProject.prepare_if_dev` в четвёртом. При развёртывании манифест тоже нужно создавать. Для автоматизации используем CI/CD.

Это требуется и при самостоятельном размещении Dagster, и в Dagster+. Исходный workflow `deploy.yml` в Dagster+ ещё не учитывает, что вместе с Dagster нужно развёртывать проект dbt.

CI/CD работает в новом окружении, поэтому перед созданием манифеста необходимо установить dbt и остальные зависимости.

Добавим в GitHub Actions шаг подготовки `manifest.json` с помощью команды `dagster-dbt project prepare-and-package` из пакета `dagster_dbt`.

1. Получите последние изменения проекта (`git fetch && git pull`) и откройте каталог `.github/workflows`.
2. Откройте `deploy.yml`.
3. Найдите шаг `Checkout for Python Executable Deploy` (в исходном примере примерно строка 38).
4. После него добавьте:

    ```yaml
    - name: Prepare DBT project for deployment
      if: steps.prerun.outputs.result == 'pex-deploy'
      run: |
        python -m pip install pip --upgrade
        cd project-repo
        pip install . --upgrade --upgrade-strategy eager
        dagster-dbt project prepare-and-package --file dagster_and_dbt/project.py
      shell: bash
    ```

Этот шаг:

1. Называется `Prepare DBT project for deployment`.
2. Обновляет установщик пакетов Python `pip`.
3. Переходит в каталог `project-repo`.
4. Устанавливает проект и обновляет зависимости.
5. Подготавливает манифест командой `dagster-dbt project prepare-and-package`, передавая файл с объектом `DbtProject`.

**Путь в исходном примере устарел:** в текущей структуре учебного проекта объект находится в `src/dagster_and_dbt/defs/project.py`. В своём workflow замените значение `--file` на этот путь. Приведённый выше исходный блок сохранён для сопоставления с оригиналом.

После отправки изменений GitHub автоматически запустит обновлённый workflow. При правильной подготовке манифеста проект будет развёрнут в Dagster+, а модели появятся в графе ассетов:

![Модели dbt в графе ассетов Dagster+](/images/dagster-dbt/lesson-7/asset-graph.png)

## Если возникли проблемы

Dagster+ Serverless поддерживает разные способы развёртывания. В этом примере изменён процесс Fast Deploys с PEX (Python Executable).

**Если сообщение об ошибке предлагает отключить Fast Deploys**, учтите: условный шаг подготовки dbt из примера тогда будет пропущен. При возможности сохраните Fast Deploys либо адаптируйте подготовку dbt к выбранному способу сборки.

**Если локально всё работает**, проверьте, совпадают ли пути создания и поиска манифеста в локальном окружении и production.

Если нужна помощь, обратитесь в канал `#dagster-university` сообщества Dagster в [Slack](https://dagster.io/slack).
