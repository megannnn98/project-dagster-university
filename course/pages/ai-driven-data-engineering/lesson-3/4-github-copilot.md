---
title: 'Урок 3: GitHub Copilot'
module: 'ai_driven_data_engineering'
lesson: '3'
---

# GitHub Copilot

Если ты используешь **GitHub Copilot** в качестве агента программирования, выполни следующие шаги, чтобы обеспечить доступность скиллов Dagster. После установки и включения можно будет использовать промпты вроде `/dagster-expert` в следующих уроках.

---

## 1. Установи GitHub Copilot

Установи [расширение GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) в VS Code и войди в аккаунт GitHub. Убедись, что установлено и [расширение GitHub Copilot Chat](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat), предоставляющее интерфейс агента.

### Включи режим агента

В этом курсе предполагается, что агент самостоятельно выполняет команды терминала и записывает файлы, а не просто предлагает изменения. В Copilot Chat переключись в **Agent mode** с помощью селектора режима в поле ввода чата (найди раскрывающийся список с надписью «Ask» или «Edit» и выбери «Agent»). Без режима агента Copilot будет предлагать команды для ручного выполнения вместо их самостоятельного запуска.

---

## 2. Добавь скиллы Dagster

Команда `npx` поставляется с Node.js. Если он не установлен, сначала [установи Node.js](https://nodejs.org).

Выполни установку с помощью CLI `npx skills`:

```bash
npx skills add dagster-io/skills
```

![Установка через npx](/images/ai-driven-data-engineering/lesson-3/npx-install.png)

---

## 3. Убедись, что скиллы Dagster включены

В панели Copilot Chat убедись, что скиллы Dagster **включены**. Необходимо как минимум:

- `dagster-expert`: для структуры проекта, CLI `dg` и шаблонов Dagster.
- `dignified-python`: для лучших практик Python.

Скиллы вызываются вводом их имени с префиксом `/` в поле Copilot Chat:

```text
/dagster-expert create a new Dagster project called university
```

Ты будешь использовать этот шаблон на протяжении оставшейся части курса.

![Скилл GitHub Copilot](/images/ai-driven-data-engineering/lesson-3/copilot-skill.png)

---

## Всё готово

После установки и включения скиллов Dagster можно переходить к уроку 4. В следующих уроках ты будешь использовать промпты, вызывающие эти скиллы, чтобы агент следовал лучшим практикам Dagster и применял `dg` для создания заготовок и валидации.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
