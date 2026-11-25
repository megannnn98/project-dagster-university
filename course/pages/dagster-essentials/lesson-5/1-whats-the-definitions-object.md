---
title: "Урок 5: Что такое объект Definitions?"
module: 'dagster_essentials'
lesson: '5'
---

# Что такое объект Definitions?

Когда ты определяешь актив, ресурс или расписание в своём развёртывании Dagster, этот объект должен входить в состав объекта `Definitions` того расположения кода, в котором ты работаешь. Каждое расположение кода может иметь только один объект Definitions. Этот объект соответствует одному расположению кода. С помощью расположений кода пользователи изолируют несколько проектов Dagster друг от друга, не создавая отдельных развёртываний. Подробнее о расположениях кода поговорим чуть позже в этом уроке.

Вернёмся к примеру с печеньем. Наши активы — сухие и жидкие ингредиенты, тесто для печенья, тесто с кусочками шоколада и, наконец, само печенье с кусочками шоколада — можно считать **определениями** (в данном случае определениями для приготовления печенья):

![Активы приготовления печенья, например сухие и жидкие ингредиенты, можно уподобить определениям Dagster](/images/dagster-essentials/lesson-5/cookie-definitions.png)

В Dagster объект `Definitions` находится в файле `definitions.py`. Если бы мы хотели создать объект `Definitions` для определений приготовления печенья, он выглядел бы примерно так:

```python
import dagster_cookies.defs as defs

defs = dg.components.load_defs(defs)
```

## Автоматическая загрузка

После появления `dg` больше не нужно явно перечислять все активы проекта в объекте `Definitions`. Dagster может автоматически загружать большинство объектов (позже мы увидим, что существуют и другие типы объектов, помимо активов), импортируя содержимое модуля `defs`.

Вспомни, что при использовании `dg scaffold` все файлы активов размещались в каталоге `defs`.

```
src
└── dagster_essentials
    ├── definitions.py
    └── defs
        └── assets
            ├── __init__.py
            ├── constants.py
            ├── metrics.py
            └── trips.py
```

В этом курсе у тебя будет только одно расположение кода (и, соответственно, один объект `Definitions`). Однако по мере роста проекта необходимо следить за тем, чтобы объект `Definitions` включал новые определения.

---

## Как Dagster использует объект Definitions

Разобравшись с тем, что такое объект `Definitions`, рассмотрим, как Dagster его использует.

При запуске `dg dev` Dagster обращается к файлу `pyproject.toml`. В этом файле содержатся зависимости Python, необходимые для запуска Dagster, а также специфичные для Dagster настройки, указывающие, откуда загружать объект `Definitions`.

```yaml
[tool.dg]
directory_type = "project"

[tool.dg.project]
root_module = "dagster_essentials"
registry_modules = [
    "dagster_essentials.components.*",
]
```

Открой в своём проекте файл `dagster_university/dagster_essentials/src/dagster_essentials/definitions.py`. Он должен выглядеть примерно так:

```python
# src/dagster_essentials/definitions.py
from pathlib import Path

from dagster import definitions, load_from_defs_folder


@definitions
def defs():
    return load_from_defs_folder(project_root=Path(__file__).parent.parent.parent)
```

**Примечание:** файл `definitions.py` автоматически генерируется при создании каркаса нового проекта Dagster с помощью [`uvx`](https://docs.dagster.io/getting-started/installation).

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
