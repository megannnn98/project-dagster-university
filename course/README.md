# Dagster University

В этом каталоге находятся материалы Dagster University, опубликованного по адресу https://courses.dagster.io. Сайт построен на [NextJS](https://nextjs.org/) и [Markdoc](https://markdoc.dev/).

---

## Настройка

Сначала клонируй репозиторий, перейди в каталог `course` и установи необходимые зависимости:

```bash
npm install
# or
yarn install
```

Чтобы запустить сайт локально в режиме разработки (с автоматической перезагрузкой), выполни:

```bash
npm run dev
# or
yarn dev
```

Открой [http://localhost:3000](http://localhost:3000) в браузере, чтобы увидеть результат.

### Публикация на GitHub Pages

В [Settings → Pages](https://github.com/megannnn98/project-dagster-university/settings/pages) выбери **Source → GitHub Actions**. Если Actions отключены в форке, сначала включи их на вкладке Actions. Затем запусти workflow **Russian Dagster University — GitHub Pages** из ветки `main`. При изменениях в каталоге `course` сайт будет автоматически пересобираться и публиковаться.

Локальная проверка того же статического экспорта (Linux/macOS):

```bash
DAGSTER_STATIC_EXPORT=1 NEXT_PUBLIC_BASE_PATH=/project-dagster-university yarn build
python3 scripts/check-pages-export.py out /project-dagster-university
```

Результат находится в `course/out`. Для локальной разработки через `yarn dev` эти переменные не нужны.

### Проверка ссылок

Чтобы проверить корректность внутренних и внешних ссылок в Markdown-файлах курса:

```bash
yarn linkcheck
```

Команда запускает проверку внутренних ссылок (соответствие маршрутов Next.js существующим страницам) и [markdown-link-check](https://www.npmjs.com/package/markdown-link-check) для внешних URL. Внутренние ссылки, начинающиеся с `/`, и пути изображений проверяются относительно дерева `pages/`; внешние ссылки проверяются HTTP-запросами. Конфигурация находится в `.markdown-link-check.json`.

---

## Подготовка материалов

Материалы курсов находятся в каталоге `course/pages` (в исходном описании: `/dagster-university/pages`). У каждого курса есть:

- Страница категории в корне каталога, например `/../../dagster-essentials.md`. На неё добавляются ссылки на отдельные уроки для удобной навигации при локальном запуске сайта.
- Отдельный подкаталог, например `/../../dagster-essentials`, содержащий папку для каждого урока курса.

### Содержание уроков

Предпочитаешь учиться на примерах? Посмотри этот PR, чтобы узнать, как [добавить новый урок в курс](https://github.com/dagster-io/dagster/pull/20096).

### Форматирование Markdown

Для подготовки материалов мы используем [Markdoc](https://markdoc.dev/) — разновидность Markdown, похожую на Markdown в GitHub, но с дополнительными возможностями. Подробнее см. [документацию по синтаксису Markdoc](https://markdoc.dev/docs/syntax).

#### Таблицы

Поддерживаются таблицы CommonMark, но для создания таблиц можно также использовать форматирование списков. Например:

```markdown
## commonmark table

| Name  | ID | Description                |
|-------|----|----------------------------|
| Daggy | 1  | The most educated octopus. |
```

В синтаксисе Markdoc это выглядит так:

```markdown
## markdoc table 

{% table %}
* Name
* ID
* Description
---
* Daggy
* 1
* The most educated octopus.
{% /table %}
```

Дополнительную информацию и примеры см. в [документации по таблицам Markdoc](https://markdoc.dev/docs/tags#table).

---

## Получение помощи

- Присоединяйся к сообществу [Dagster Slack](https://dagster.io/community) и задавай вопросы в канале `#dagster-university`.
- Ищи решения и шаблоны в [обсуждениях GitHub](https://github.com/dagster-io/dagster/discussions).
- Обращайся к [документации Dagster](https://docs.dagster.io/).

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
