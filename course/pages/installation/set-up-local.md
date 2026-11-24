---
title: "Урок 2: Локальная настройка"
lesson: '2'
---

# Локальная настройка

Эта инструкция поможет настроить Dagster на твоём компьютере. Если ты предпочитаешь проходить курс в GitHub Codespaces, воспользуйся [соответствующей инструкцией](/installation/set-up-codespace).

- **Установить Git.** Если Git ещё не установлен, обратись к [документации Git](https://github.com/git-guides/install-git).
- **Установить Python.** Для этого курса поддерживаются Python 3.10–3.13 (рекомендуется 3.12).
- **Установить менеджер пакетов.** Для управления пакетами Python мы рекомендуем [`uv`](https://docs.astral.sh/uv/), который используется и в самом Dagster.

---

## Клонирование проекта Dagster University

[Клонируй репозиторий GitHub](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository). Команда зависит от выбранного способа клонирования: [SSH или HTTPS](https://graphite.dev/guides/git-clone-ssh-vs-https).

| Вариант | Команда |
| --- | --- |
| ssh | ```git clone git@github.com:dagster-io/project-dagster-university.git``` |
| https | ```git clone https://github.com/dagster-io/project-dagster-university.git``` |

После клонирования проекта Dagster University перейди в каталог нужного курса внутри репозитория. Все курсы находятся в папке `dagster_university`.

Например, если ты проходишь Dagster Essentials, перейди в соответствующий каталог:

```bash
cd project-dagster-university/dagster_university/dagster_essentials
```

## Установка зависимостей

**uv**

Если [`uv`](https://docs.astral.sh/uv/) ещё не установлен, это можно сделать [несколькими способами](https://docs.astral.sh/uv/getting-started/installation/). Для установки зависимостей Python с помощью `uv` выполни следующую команду из каталога выбранного курса:

```bash
uv sync
```

Команда создаст виртуальное окружение и установит необходимые зависимости. Для активации созданного виртуального окружения используй соответствующую команду:

| ОС | Команда |
| --- | --- |
| Linux / macOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

---

**pip**

Для установки зависимостей Python с помощью [pip](https://pypi.org/project/pip/) выполни следующую команду из каталога выбранного курса:

```bash
python3 -m venv .venv
```

Команда создаст виртуальное окружение. Для его активации:

| ОС | Команда |
| --- | --- |
| Linux / macOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

Чтобы установить необходимые зависимости, выполни:

```bash
pip install -e ".[dev]"
```

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
