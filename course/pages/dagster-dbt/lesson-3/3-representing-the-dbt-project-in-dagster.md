---
title: "Урок 3: Представление проекта dbt в Dagster"
module: 'dagster_dbt'
lesson: '3'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Представление проекта dbt в Dagster

В этом курсе код Dagster будет часто обращаться к проекту dbt и файлу `target/manifest.json`. Удобно создать переиспользуемое представление проекта с помощью класса `DbtProject`.

> 📝 **Примечание:** файл `defs/project.py` уже есть в начальном проекте, но пока пуст. Весь приведённый ниже код нужно добавить в него.

Добавьте импорты в `defs/project.py`:

```python
# src/dagster_and_dbt/defs/project.py
from pathlib import Path

from dagster_dbt import DbtProject
```

Класс `Path` из стандартного модуля `pathlib` поможет задать точный путь к проекту dbt. Класс `DbtProject` импортируется из установленного ранее пакета `dagster_dbt`.

После импортов добавьте:

```python
dbt_project = DbtProject(
  project_dir=Path(__file__).joinpath("../..", "analytics").resolve(),
)
```

Этот код создаёт представление проекта под именем `dbt_project`. Разберём выражение, задающее каталог:

- Путь к файлу `project.py`, доступный через `__file__`, служит отправной точкой.
- Аргументы `joinpath` добавляют к этому пути:
   - Переход на два уровня вверх (`"../.."`). Поскольку исходный путь включает имя файла, это приводит к каталогу `src/dagster_and_dbt`.
   - Имя каталога `analytics`, содержащего проект dbt.
- Метод `resolve` преобразует результат в абсолютный путь, не зависящий от текущего рабочего каталога.

Полный файл `defs/project.py` должен выглядеть так:

```python
# src/dagster_and_dbt/defs/project.py
from pathlib import Path

from dagster_dbt import DbtProject

dbt_project = DbtProject(
    project_dir=Path(__file__).joinpath("../..", "analytics").resolve(),
)
```

> 💡 **Застряли?** Сравните свой код с готовым примером в `src/dagster_and_dbt/completed/lesson_3/defs/project.py`.

Теперь представление `dbt_project` можно использовать из других файлов. Начнём с создания ресурса Dagster, который будет запускать dbt.
