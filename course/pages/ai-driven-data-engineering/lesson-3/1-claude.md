---
title: 'Урок 3: Claude Code'
module: 'ai_driven_data_engineering'
lesson: '3'
---

# Claude Code

Если ты используешь **Claude Code** в качестве агента программирования, выполни следующие шаги, чтобы обеспечить доступность скиллов Dagster. После установки и включения можно будет использовать промпты вроде `/dagster-expert` в следующих уроках.

---

## 1. Установи Claude Code

Установи [Claude Code](https://docs.anthropic.com/en/docs/claude-code/setup) и войди в аккаунт согласно инструкции по настройке.

---

## 2. Установи скиллы Dagster

В Claude Code добавь скиллы Dagster через каталог плагинов:

```text
/plugin marketplace add dagster-io/skills
```

![Каталог плагинов Claude](/images/ai-driven-data-engineering/lesson-3/claude-marketplace.png)

Затем установи оба скилла Dagster:

```text
/plugin install dagster-expert@dagster-skills
```

```text
/plugin install dignified-python@dagster-skills
```

---

## 3. Перезагрузи плагины

После установки перезагрузи реестр плагинов, чтобы Claude Code обнаружил новые скиллы:

```text
/reload-plugins
```

---

## 4. Убедись, что скиллы Dagster включены

Открой список плагинов и проверь, что скиллы Dagster включены:

```text
/plugin
```

Перейди на вкладку **Installed** и убедись, что скиллы Dagster отмечены как включённые. Ты должен увидеть примерно следующее:

- **dagster-expert**: включён.
- **dignified-python**: включён.

Если скилл отсутствует в списке, установи его отдельно:

```text
/plugin install dagster-expert@dagster-skills
```

```text
/plugin install dignified-python@dagster-skills
```

Затем снова выполни `/reload-plugins`, прежде чем продолжить.

Если скилл присутствует, но отключён, включи его, чтобы агент мог использовать лучшие практики Dagster и CLI `dg` при вызове скилла в промптах.

![Плагин Claude](/images/ai-driven-data-engineering/lesson-3/claude-plugin.png)

---

## Как вызывать скиллы

В Claude Code скиллы вызываются через slash-команды. Введи имя скилла с префиксом `/` в начале промпта:

```text
/dagster-expert create a new Dagster project called university
```

Claude Code загружает контекст этого скилла перед ответом. Ты будешь использовать этот шаблон на протяжении оставшейся части курса.

---

## Всё готово

После установки и включения скиллов Dagster можно переходить к уроку 4. В следующих уроках ты будешь использовать скиллы, чтобы агент следовал лучшим практикам Dagster и применял `dg` для создания заготовок и валидации.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
