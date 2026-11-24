---
title: "Урок 2: Настройка Codespace"
lesson: '2'
---

# Настройка с помощью GitHub Codespaces

Вместо настройки локального окружения можно воспользоваться [GitHub Codespaces](https://github.com/features/codespaces). Это позволит проходить курс и редактировать код репозитория в облачном окружении.

## Создание GitHub Codespace

Для разных курсов Dagster University предусмотрены отдельные конфигурации Codespaces. При создании Codespace убедись, что выбрана конфигурация нужного курса.

1. Войди в аккаунт GitHub и перейди на [страницу Codespaces](https://github.com/codespaces).
2. В правом верхнем углу выбери «New Codespace».
3. Создай Codespace, используя следующие параметры.

    | Поле | Значение |
    |--- | --- |
    | Repository | dagster-io/project-dagster-university |
    | Branch | main |
    | Dev container configuration | Название нужного курса |
    | Region | US East |
    | Machine type | 2-core |

    ![Создание Codespace](/images/shared/codespaces/codespaces-create.png)

4. Нажми «Create codespace».

При первом создании Codespace запуск всех компонентов может занять некоторое время. Затем откроется интерактивный редактор с кодом всего репозитория Dagster University.

## Работа в Codespace

В терминале в нижней части IDE перейди в каталог нужного курса. Например, если ты проходишь Dagster Essentials, перейди в следующий каталог:

```bash
cd dagster_university/dagster_essentials
```

Чтобы убедиться, что всё работает, запусти пользовательский интерфейс Dagster.

```bash
dg dev
```

После запуска Dagster появится предложение открыть интерфейс в браузере. Нажми «Open in Browser».

![Запуск Dagster в Codespace](/images/shared/codespaces/codespaces-launch.png)

## Остановка GitHub Codespace

Обязательно останавливай Codespace, когда не используешь его. Согласно оригинальному курсу, GitHub предоставляет личным аккаунтам [120 ядро-часов в месяц](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-codespaces/about-billing-for-github-codespaces#monthly-included-storage-and-core-hours-for-personal-accounts).

![Остановка Codespace](/images/shared/codespaces/codespaces-stop.png)

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
