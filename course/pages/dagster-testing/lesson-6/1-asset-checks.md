---
title: 'Урок 6: Проверки ассетов'
module: 'dagster_testing'
lesson: '6'
---

# Проверки ассетов

Один из ключевых аспектов тестирования данных — валидация и контроль качества. Такие проверки отличаются от модульных и интеграционных тестов. Вместо выполнения вне основного приложения до развёртывания кода проверки данных существуют в рабочем окружении вместе с ассетами.

При проектировании этапов валидации данных лучше отделять их код от основной логики ассетов. Это даёт больше гибкости при обработке проблем валидации и помогает переиспользовать отдельные элементы.

Для решения задачи контроля качества данных Dagster предоставляет проверки ассетов (asset checks), которые позволяют проверять ассеты при выполнении. Проверки являются частью проекта Dagster и регистрируются в Definitions, как и другие объекты Dagster. На графе ассетов они не отображаются отдельными узлами, а связаны с соответствующим ассетом.

# Определение проверок ассетов

Для определения проверки сначала нужен ассет. `total_population` — немного изменённая версия ассета, который мы использовали на протяжении курса. Теперь он принимает результаты нескольких ассетов и суммирует население.

```python
# src/dagster_testing/defs/assets/lesson_6.py
@dg.asset
def total_population(
    state_population_file_config: list[dict],
    state_population_api_resource: list[dict],
) -> int:
    all_assets = state_population_file_config + state_population_api_resource
    return sum([int(x["Population"]) for x in all_assets])
```

Допустим, мы хотим проверить, что число, возвращаемое `total_population`, всегда положительное. Определим проверку ассета с помощью декоратора `dg.asset_check`. В декораторе свяжем её с `total_population`.

```python
@dg.asset_check(asset=total_population)
```

Теперь `total_population` можно использовать как входной параметр самой функции. Вот как может выглядеть проверка ассета. Нажми **View answer**, чтобы посмотреть ответ.

```python {% obfuscated="true" %}
# src/dagster_testing/defs/assets/lesson_6.py
@dg.asset_check(asset=total_population)
def non_negative(total_population):
    return dg.AssetCheckResult(
        passed=bool(total_population > 0),
    )
```

Функция проверяет, что результат `total_population` больше нуля, и передаёт результат проверки в `AssetCheckResult`, который будет зарегистрирован в истории метаданных Dagster.

# Тестирование проверок ассетов

Для кода проверок ассетов также можно писать модульные тесты. В зависимости от сложности проверок полезно иметь тесты, подтверждающие корректность валидации ассетов.

Написание теста для проверки ассета похоже на написание теста для самого ассета. В качестве входного параметра передаём проверяемое значение, а затем определяем, прошёл ли ассет валидацию.

```python
# tests/test_lesson_6.py
def test_non_negative():
    asset_check_pass = lesson_6.non_negative(10)
    assert asset_check_pass.passed
    asset_check_fail = lesson_6.non_negative(-10)
    assert not asset_check_fail.passed
```

```bash
> pytest tests/test_lesson_6.py::test_non_negative
...
tests/test_lesson_6.py .                                                          [100%]
```

# Блокирующие проверки ассетов

По умолчанию проверки выполняются вместе с материализацией ассетов и сообщают свои результаты. Однако можно использовать `blocking=True`, чтобы предотвратить материализацию нижестоящих ассетов при провале блокирующей проверки с уровнем серьёзности ERROR. Это полезно для критических проверок качества данных.

```python
@dg.asset_check(asset=raw_data, blocking=True)
def validate_schema(raw_data: list[dict]) -> dg.AssetCheckResult:
    """Block downstream processing if schema is invalid."""
    required_columns = {"id", "name", "email"}
    actual_columns = set(raw_data[0].keys()) if raw_data else set()

    passed = required_columns.issubset(actual_columns)

    return dg.AssetCheckResult(
        passed=passed,
        metadata={
            "required_columns": list(required_columns),
            "actual_columns": list(actual_columns),
        },
    )
```

**Когда использовать блокирующие проверки**:
- Валидация схемы перед преобразованием.
- Критические проверки качества данных.
- Проверка предварительных условий дорогостоящих нижестоящих операций.

# Уровень серьёзности проверки ассета

Проверки ассетов могут сообщать разные уровни серьёзности, чтобы указать важность обнаруженной проблемы. Используй `dg.AssetCheckSeverity`, чтобы различать ошибки и предупреждения.

```python
@dg.asset_check(asset=my_data)
def row_count_check(my_data: list) -> dg.AssetCheckResult:
    row_count = len(my_data)
    
    if row_count == 0:
        return dg.AssetCheckResult(
            passed=False,
            severity=dg.AssetCheckSeverity.ERROR,
            metadata={"row_count": 0},
        )
    elif row_count < 100:
        return dg.AssetCheckResult(
            passed=True,  # Warning, not failure
            severity=dg.AssetCheckSeverity.WARN,
            metadata={"row_count": row_count, "message": "Low row count"},
        )
    else:
        return dg.AssetCheckResult(
            passed=True,
            metadata={"row_count": row_count},
        )
```

Уровень `WARN` позволяет отмечать потенциальные проблемы как предупреждения, не блокируя нижестоящие ассеты даже при `blocking=True`. Сам результат проверки при этом всё равно может быть отрицательным (`passed=False`). Это полезно для мягких порогов и рекомендательных условий.

# Групповые проверки ассетов

Если несколько проверок работают с одними и теми же данными, эффективнее загрузить ассет один раз и выполнить все проверки вместе. Для этого используй `@dg.multi_asset_check`.

```python
@dg.multi_asset_check(
    specs=[
        dg.AssetCheckSpec(name="unique_ids", asset="customer_data"),
        dg.AssetCheckSpec(name="no_null_emails", asset="customer_data"),
    ]
)
def customer_data_checks(customer_data: list[dict]):
    """Run multiple checks in a single execution."""
    ids = [row["id"] for row in customer_data]
    unique_count = len(set(ids))
    total_count = len(ids)

    yield dg.AssetCheckResult(
        check_name="unique_ids",
        passed=unique_count == total_count,
        metadata={"duplicates": total_count - unique_count},
    )

    null_emails = sum(1 for row in customer_data if row["email"] is None)

    yield dg.AssetCheckResult(
        check_name="no_null_emails",
        passed=null_emails == 0,
        metadata={"null_count": null_emails},
    )
```

**Используй `@multi_asset_check`, когда**:
- Несколько проверок работают с одними и теми же данными.
- Загрузка ассета требует значительных ресурсов.
- Проверки используют общую вычислительную логику.

# Партиционированные проверки ассетов

Если ассеты партиционированы и нужно проверять каждую партицию независимо — обнаруживать проблемы в конкретном диапазоне дат или регионе, не затрагивая остальные партиции, — используй партиционированную проверку ассета.

Добавь `partitions_def` в `@dg.asset_check` с тем же определением `PartitionsDefinition`, что и у ассета:

```python
file_partitions = dg.StaticPartitionsDefinition(["ca.csv", "mn.csv", "ny.csv"])

@dg.asset_check(asset=population_file_partition, partitions_def=file_partitions)
def partition_has_data(population_file_partition: list[dict]) -> dg.AssetCheckResult:
    row_count = len(population_file_partition)
    return dg.AssetCheckResult(
        passed=row_count > 0,
        metadata={"row_count": row_count},
    )
```

Dagster выполняет такую проверку для каждой выбранной партиции. При соответствующем сопоставлении входов функция получает данные этой партиции, поэтому логика остаётся простой — дополнительная фильтрация не требуется.

Тестирование партиционированной проверки следует тому же шаблону, что и тестирование любой другой проверки: вызови функцию напрямую с репрезентативными данными.

```python
def test_partition_has_data(file_output):
    result = lesson_6.partition_has_data(file_output)
    assert result.passed
    assert result.metadata["row_count"].value == 3

def test_partition_has_data_empty():
    result = lesson_6.partition_has_data([])
    assert not result.passed
```

```bash
> pytest tests/test_lesson_6.py::test_partition_has_data tests/test_lesson_6.py::test_partition_has_data_empty
...
tests/test_lesson_6.py ..                                                         [100%]
```

# Фабричный шаблон для проверок ассетов

Если нужно применить одинаковую логику проверки к нескольким ассетам или столбцам, используй фабричную функцию для программной генерации проверок.

```python
def create_not_null_check(asset_name: str, column: str):
    """Factory to create not-null checks for any column."""
    @dg.asset_check(asset=asset_name, name=f"{column}_not_null")
    def check_fn(asset_value: list[dict]) -> dg.AssetCheckResult:
        null_count = sum(1 for row in asset_value if row.get(column) is None)
        return dg.AssetCheckResult(
            passed=null_count == 0,
            metadata={"null_count": null_count, "column": column},
        )
    return check_fn

# Generate checks
email_check = create_not_null_check("customer_data", "email")
name_check = create_not_null_check("customer_data", "name")
```

Этот шаблон сокращает дублирование кода и упрощает поддержание согласованных правил валидации во всём проекте.

_Русский перевод оригинального материала Dagster University; текст изменён при переводе._
