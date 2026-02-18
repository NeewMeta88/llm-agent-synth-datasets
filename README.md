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
