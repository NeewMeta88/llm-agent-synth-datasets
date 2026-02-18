# Dataset Generator — синтетические датасеты для тестирования LLM-агентов

Генератор превращает “сырой” markdown с бизнес-описанием в набор артефактов для eval’ов:

- `use_cases.json` — извлечённые use cases (+ evidence/traceability)
- `policies.json` — правила/ограничения (+ evidence/traceability)
- `test_cases.json` — тест-кейсы (параметры + ссылки на policy)
- `dataset.json` — примеры с `expected_output`, `evaluation_criteria`, `policy_ids`
- `run_manifest.json` — параметры запуска (seed, провайдер/модель LLM и т.д.)

Проект покрывает два обязательных кейса:
1) **support-bot** (FAQ + тикеты)  
2) **operator-quality** (контекстные/бесконтекстные проверки)

---

## Стек

- Python 3.13
- Typer
- Pydantic
- JSON Schema + jsonschema
- Ollama через OpenAI SDK

---

## Ожидаемая структура результатов

После генерации в репозитории должны появиться директории:

```text
out/
  support/
    run_manifest.json
    use_cases.json
    policies.json
    test_cases.json
    dataset.json
  operator_quality/
    run_manifest.json
    use_cases.json
    policies.json
    test_cases.json
    dataset.json
```

---

## Быстрый старт (по шагам)

### 1) Клонирование репозитория

Windows (cmd):

```bat
git clone <REPO_URL>
cd llm-agent-synth-datasets
```

macOS/Linux:

```bash
git clone <REPO_URL>
cd llm-agent-synth-datasets
```

### 2) Python окружение

Windows (cmd):

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3) Установка зависимостей

Windows (cmd):

```bat
python -m pip install -e .
```

macOS/Linux:

```bash
python -m pip install -e .
```

### 4) `.env`

Создайте `.env` из шаблона (CLI-аргументы имеют приоритет над `.env`).

Windows (cmd):

```bat
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Для Ollama можно задать в `.env`:

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`

---

## Входные документы

Сырые входы кладите в `examples/`.

Обязательные файлы:

- `examples/example_input_raw_support_faq_and_tickets.md`
- `examples/example_input_raw_operator_quality_checks.md`

Опционально:

- `examples/example_input_raw_doctor_booking.md`

Если примеры хранятся в ТЗ — можно синхронизировать их в `examples/`:

Windows (cmd):

```bat
python tools\extract_examples_from_tz.py
```

macOS/Linux:

```bash
python tools/extract_examples_from_tz.py
```

---

## Запуск с LLM — Ollama

### 1) Установка и запуск Ollama

Установите [Ollama](https://ollama.com/download) как приложение и запустите сервис.

### 2) Скачайте модель

Пример:

Windows (cmd):

```bat
ollama pull llama3.2
```

macOS/Linux:

```bash
ollama pull llama3.2
```

### 3) Генерация артефактов

**Support-bot:**

Windows (cmd):

```bat
python -m dataset_generator ^
  --llm-provider ollama ^
  --llm-model llama3.2 ^
  --input examples\example_input_raw_support_faq_and_tickets.md ^
  --out out\support ^
  --seed 42
```

macOS/Linux:

```bash
python -m dataset_generator \
  --llm-provider ollama \
  --llm-model llama3.2 \
  --input examples/example_input_raw_support_faq_and_tickets.md \
  --out out/support \
  --seed 42
```

**Operator-quality:**

Windows (cmd):

```bat
python -m dataset_generator ^
  --llm-provider ollama ^
  --llm-model llama3.2 ^
  --input examples\example_input_raw_operator_quality_checks.md ^
  --out out\operator_quality ^
  --seed 42
```

macOS/Linux:

```bash
python -m dataset_generator \
  --llm-provider ollama \
  --llm-model llama3.2 \
  --input examples/example_input_raw_operator_quality_checks.md \
  --out out/operator_quality \
  --seed 42
```

**Doctor-booking (optional):**

Windows (cmd):

```bat
python -m dataset_generator ^
  --llm-provider ollama ^
  --llm-model llama3.2 ^
  --input examples\example_input_raw_doctor_booking.md ^
  --out out\doctor_booking ^
  --seed 42
```

macOS/Linux:

```bash
python -m dataset_generator \
  --llm-provider ollama \
  --llm-model llama3.2 \
  --input examples/example_input_raw_doctor_booking.md \
  --out out/doctor_booking \
  --seed 42
```

Подсказка: доступные CLI-опции смотрите так:

Windows (cmd):

```bat
python -m dataset_generator --help
```

macOS/Linux:

```bash
python -m dataset_generator --help
```

---

## Валидация результатов

Windows (cmd):

```bat
python -m dataset_generator validate --out out\support
python -m dataset_generator validate --out out\operator_quality
```

macOS/Linux:

```bash
python -m dataset_generator validate --out out/support
python -m dataset_generator validate --out out/operator_quality
```

---

## Проверки

Windows (cmd):

```bat
python -m pytest -q
python -m dataset_generator validate --out out\support
python -m dataset_generator validate --out out\operator_quality
python scripts\run_official_validator.py --support-out out\support --operator-out out\operator_quality
```

macOS/Linux:

```bash
python -m pytest -q
python -m dataset_generator validate --out out/support
python -m dataset_generator validate --out out/operator_quality
python scripts/run_official_validator.py --support-out out/support --operator-out out/operator_quality
```

---

## Fallback: если LLM недоступна / не настроена

Если Ollama недоступна (сервис не запущен) или модель не найдена, генератор автоматически продолжит работу **без LLM**.  
Это фиксируется в `out/*/run_manifest.json`.

Если вам нужно **принудительно отключить LLM** (например, для отладки), можно запустить так:

Windows (cmd):

```bat
python -m dataset_generator ^
  --llm-provider none ^
  --input examples\example_input_raw_support_faq_and_tickets.md ^
  --out out\support ^
  --seed 42
```

macOS/Linux:

```bash
python -m dataset_generator \
  --llm-provider none \
  --input examples/example_input_raw_support_faq_and_tickets.md \
  --out out/support \
  --seed 42
```

---

## Troubleshooting

### 1) Ошибка подключения к Ollama

- Убедитесь, что Ollama запущена как сервис/приложение.
- Проверьте `OLLAMA_BASE_URL` (если переопределяли) или используйте CLI-аргументы.

### 2) Модель не найдена

- Скачайте модель: `ollama pull <model>`
- Либо укажите корректное имя модели через `--llm-model`.

### 3) Генерация “пошла без LLM”

- Это ожидаемо при недоступной/не настроенной LLM.
- Проверьте `run_manifest.json` в папке соответствующего прогона.

---

## Пример вывода

### 1) dataset.json

```json
{
      "case": "support_bot",
      "evaluation_criteria": [
        "helpfulness",
        "clarity",
        "politeness"
      ],
      "expected_output": "Мы признательны за обращение к нам. Важно для нас здоровье и благополучие вашего ребенка. Кто может предоставить больше информации о проблемах, с которыми сталкивается ваш ребенок?",
      "format": "single_turn_qa",
      "id": "ex_tcuc2-complexity-tickets",
      "input": {
        "messages": [
          {
            "content": "ребёнку 10 лет, к педиатру",
            "role": "user"
          }
        ],
        "target_message_index": null
      },
      "metadata": {
        "source": "tickets",
        "split": "train"
      },
      "policy_ids": [
        "pol__3"
      ],
      "test_case_id": "tc_uc2-complexity",
      "use_case_id": "uc__2"
    }
```

### 2) policies.json

```json
"policies": [
    {
      "case": "support_bot",
      "evidence": [
        {
          "input_file": "example_input_raw_doctor_booking.md",
          "line_end": 13,
          "line_start": 13,
          "quote": "В общем, бот не должен светить личные номера врачей. Ну и контакты пациентов тоже. Если кто-то просит «дай телефон доктора» — только запись через систему либо общий номер регистратуры 8-800-XXX."
        }
      ],
      "id": "pol_",
      "statement": "Бот не должен предоставлять личные номера врачей или контактную информацию пациентов.",
      "type": "must"
    },
    {
      "case": "support_bot",
      "evidence": [
        {
          "input_file": "example_input_raw_doctor_booking.md",
          "line_end": 17,
          "line_start": 17,
          "quote": "Рабочие часы: пн–пт 9:00–18:00 по местному времени. В субботу только с 10 до 14\\. В воскресенье приём не ведётся. Если пишут ночью или в выходные — говорим расписание и предлагаем оставить заявку. Звонок в нерабочее время — тот же сценарий."
        }
      ],
      "id": "pol_arrives-early-enough",
      "statement": "Бот должен предложить срочный приём, если заявка arrives early enough.",
      "type": "must"
    },
    {
      "case": "support_bot",
      "evidence": [
        {
          "input_file": "example_input_raw_doctor_booking.md",
          "line_end": 33,
          "line_start": 33,
          "quote": "5. **Чеки, справки, рецепты** — не выдаём через чат. Только в клинике или через ЛК (если настроен). Бот не имеет доступа к ЛК.  "
        }
      ],
      "id": "pol__2",
      "statement": "Бот не должен предоставлять справки или рецепты через чат.",
      "type": "must"
    }
```

### 3) test_cases.json

```bash
"test_cases": [
    {
      "case": "support_bot",
      "description": "Test case focusing on axis: tone",
      "id": "tc_uc-tone",
      "parameters": {
        "axis": "tone"
      },
      "policy_ids": [
        "pol_"
      ],
      "use_case_id": "uc_"
    },
    {
      "case": "support_bot",
      "description": "Test case focusing on axis: tone",
      "id": "tc_uc-tone_2",
      "parameters": {
        "axis": "tone"
      },
      "policy_ids": [
        "pol_arrives-early-enough"
      ],
      "use_case_id": "uc_"
    },
    {
      "case": "support_bot",
      "description": "Test case focusing on axis: edge_case",
      "id": "tc_uc-edgecase",
      "parameters": {
        "axis": "edge_case"
      },
      "policy_ids": [
        "pol__2"
      ],
      "use_case_id": "uc_"
    }
```

### 4) use_cases.json

```bash
"use_cases": [
    {
      "case": "support_bot",
      "description": "Пользователь пишет заявку на приём к врачу.",
      "evidence": [
        {
          "input_file": "example_input_raw_doctor_booking.md",
          "line_end": 17,
          "line_start": 17,
          "quote": "Рабочие часы: пн–пт 9:00–18:00 по местному времени. В субботу только с 10 до 14\\. В воскресенье приём не ведётся. Если пишут ночью или в выходные — говорим расписание и предлагаем оставить заявку. Звонок в нерабочее время — тот же сценарий."
        }
      ],
      "id": "uc_",
      "name": "Запись на приём"
    },
    {
      "case": "support_bot",
      "description": "Пользователь хочет отменить или перенести свою запись.",
      "evidence": [
        {
          "input_file": "example_input_raw_doctor_booking.md",
          "line_end": 30,
          "line_start": 30,
          "quote": "2. **Можно ли отменить?** Да. Нужны ФИО и дата/время приёма. Ну или номер записи, если есть.  "
        }
      ],
      "id": "uc__2",
      "name": "Отмена или перенос записи"
    },
    {
      "case": "support_bot",
      "description": "Пользователь задает вопрос, который бот должен ответить.",
      "evidence": [
        {
          "input_file": "example_input_raw_doctor_booking.md",
          "line_end": 29,
          "line_start": 29,
          "quote": "1. **Как записаться?** Через сайт, чат или по телефону 8-800-XXX. В чате — напишите желаемую дату, время, специализацию (терапевт, кардиолог и т.д.).  "
        }
      ],
      "id": "uc__3",
      "name": "Вопросы и ответы"
    }
    
```

### 5) run_manifest.json

```bash
{
  "generator_version": "0.1.0",
  "input_path": "examples\\example_input_raw_doctor_booking.md",
  "llm": {
    "model": "llama3.2",
    "provider": "ollama",
    "temperature": 0.2
  },
  "out_path": "out\\doctor_booking",
  "seed": 42,
  "timestamp": "2026-02-18T06:55:19.382437+00:00"
}

```

