---
title: "Урок 7: Настройка Dagster+"
module: 'dbt_dagster'
lesson: '7'
---

<!-- Неофициальный русский перевод; исходный материал изменён. -->

# Настройка Dagster+

Проект готов на GitHub — перейдём к Dagster+. Для простоты используем [Serverless-развёртывание](https://docs.dagster.io/dagster-plus/deployment/serverless): управление инфраструктурой берёт на себя Dagster Labs.

1. Зарегистрируйте [пробную учётную запись Dagster+](https://dagster.cloud/signup). В оригинале курса предлагается отдельная учётная запись даже при наличии существующей. Там также указано, что пробный период начинается автоматически, а списания после него требуют добавленной банковской карты; актуальные условия проверьте при регистрации.
2. Завершите регистрацию: создайте организацию и заполните профиль.
3. При выборе типа развёртывания нажмите **Serverless**.
4. Выберите **Import a Dagster project**:
    1. В **Git scope** укажите аккаунт или организацию GitHub, где находится проект.

       {% callout %}
       > 💡 **Нужного аккаунта или организации нет в списке?** Возможно, сначала нужно установить GitHub-приложение Dagster+. Нажмите **+ Add account or organization**, завершите настройку на GitHub и вернитесь в Dagster+. Для установки в организацию компании может потребоваться согласование её администратора GitHub.
       {% /callout %}

    2. В **Repository** выберите репозиторий проекта Dagster.
    3. Нажмите **Deploy**. Развёртывание может занять несколько минут.

---

## Что происходит при развёртывании кода в Dagster+

- В окружении `prod` создаётся расположение кода для репозитория.
- В репозиторий добавляются два файла GitHub Actions:
    - `.github/workflows/deploy.yml` настраивает непрерывное развёртывание (CD). При изменении ветки `main` workflow собирает проект Dagster и развёртывает его в Dagster+.
    - `.github/workflows/branch_deployments.yml` включает [Branch Deployments](https://docs.dagster.io/deployment/dagster-plus/deploying-code/branch-deployments): отдельные проверочные окружения кода для pull request. В этом уроке они не используются, но их можно изучить отдельно.

---

## Проверка состояния развёртывания

Процесс завершился, но развёртывание не удалось. В журнале GitHub Actions, на шаге **Python Executable Deploy**, можно увидеть такую ошибку:

```yaml
Error: Some locations failed to load after being synced by the agent:
Error loading dagster_university: {'__typename': 'PythonError', 'message': "FileNotFoundError: [Errno 2] No such file or directory: '/venvs/3eca07cc1eb5/lib/python3.8/site-packages/working_directory/root/analytics/target/manifest.json'\n" ...
```

Dagster не нашёл манифест dbt. В следующем разделе исправим это.
