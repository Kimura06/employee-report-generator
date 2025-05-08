# Employee Payout Report Generator

Скрипт для генерации отчетов по заработной плате сотрудников на основе данных из CSV файлов.

## Описание

Этот скрипт обрабатывает CSV файлы с данными сотрудников и формирует отчеты различных типов. В текущей версии поддерживается отчет по заработной плате (`payout`), но архитектура скрипта позволяет легко добавлять новые типы отчетов.

## Требования

- Python 3.6+
- (Для тестов) pytest

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/employee-report-generator.git
cd employee-report-generator
```

2. Установите зависимости для тестирования:
```bash
pip install -r requirements.txt
```

## Использование

Базовый синтаксис:
```bash
python main.py [файлы CSV] --report тип_отчета
```

Пример:
```bash
python main.py data1.csv data2.csv data3.csv --report payout
```

### Формат входных файлов

Входные файлы должны быть в формате CSV и содержать следующие колонки:
- `id` - идентификатор сотрудника
- `email` - email сотрудника
- `name` - имя сотрудника
- `department` - отдел
- `hours_worked` - отработанные часы
- `hourly_rate` (или `rate`, или `salary`) - почасовая ставка

Пример входного файла:
```
id,email,name,department,hours_worked,hourly_rate
1,alice@example.com,Alice Johnson,Marketing,160,50
2,bob@example.com,Bob Smith,Design,150,40
3,carol@example.com,Carol Williams,Design,170,60
```

### Формат выходных данных

Пример выходного отчета по зарплатам:
```
                  name            hours   rate   payout
Design
-------------- Bob Smith            150      40     $6000
-------------- Carol Williams      170      60     $10200
                                               320               $16200
Marketing
-------------- Alice Johnson       160      50     $8000
                                               160               $8000

Total hours: 480
Total payout: $24200
```

## Расширение функциональности

Для добавления нового типа отчета, например отчета по средней ставке в час по отделам:

1. Создайте новую функцию генерации отчета в файле `main.py`:
```python
def generate_avg_hourly_rate_report(employees_data):
    """Generate report showing average hourly rate by department"""
    # Логика генерации отчета
    return report_text
```

2. Добавьте новую функцию в словарь `report_generators` в функции `get_report_generator`:
```python
report_generators = {
    'payout': generate_payout_report,
    'avg_rate': generate_avg_hourly_rate_report,
}
```

3. Запустите скрипт с новым типом отчета:
```bash
python main.py data1.csv data2.csv --report avg_rate
```

## Тестирование

Запуск тестов:
```bash
pytest -v
```

## Структура проекта

- `main.py` - основной скрипт
- `test_main.py` - тесты
- `requirements.txt` - зависимости для тестирования
- `README.md` - документация