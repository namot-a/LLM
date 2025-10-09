# ⚡ Первый запуск - Шаг за шагом

Это подробная инструкция для тех, кто запускает проект впервые.

## ✅ Предварительные требования

Убедитесь что установлено:
- ✅ Python 3.13+ (`python --version`)
- ✅ Node.js 20+ (`node --version`)
- ✅ PostgreSQL 12+ с pgvector
- ✅ Git

Получите:
- ✅ Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- ✅ Notion API Token ([My integrations](https://www.notion.so/my-integrations))
- ✅ OpenAI API Key ([API Keys](https://platform.openai.com/api-keys))
- ✅ PostgreSQL Database URL

## 📝 Шаг 1: Клонирование и установка

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd notiontgLLM

# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
```

**✓ Проверка:** Команда `pip list` должна показать установленные пакеты.

## 📝 Шаг 2: Настройка Backend

```bash
# Создайте .env файл
cp .env.example .env

# Откройте в редакторе
# macOS:
open .env
# Linux:
nano .env
# Windows:
notepad .env
```

**Заполните .env:**

```env
# Telegram (обязательно)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz  # От @BotFather
ALLOWED_TELEGRAM_USER_IDS=123456789                        # Ваш Telegram ID
WEBHOOK_SECRET_PATH=my-super-secret-webhook-path-2024     # Любая секретная строка

# Notion (обязательно)
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxx                  # От Notion
NOTION_DATABASE_IDS=abc123def456                           # ID вашей базы данных

# OpenAI (обязательно)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx          # От OpenAI
OPENAI_CHAT_MODEL=gpt-4o-mini                             # Или gpt-4, gpt-3.5-turbo
OPENAI_EMBED_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536

# Database (обязательно)
DATABASE_URL=postgresql://user:password@localhost:5432/notion_bot

# API Settings (можно оставить по умолчанию)
API_URL=http://localhost:8000
HOST=0.0.0.0
PORT=8000

# Retrieval (можно оставить по умолчанию)
TOP_K=6
SIMILARITY_THRESHOLD=0.25
MAX_CONTEXT_CHARS=12000

# Pricing (можно оставить по умолчанию)
PRICE_PROMPT_PER_1K=0.005
PRICE_COMPLETION_PER_1K=0.015

# Logging (можно оставить по умолчанию)
LOG_LEVEL=INFO
```

**✓ Проверка:** Файл `.env` существует и все обязательные поля заполнены.

## 📝 Шаг 3: Запуск Backend

```bash
# Убедитесь что виртуальное окружение активировано
# Должно быть (venv) в начале строки

# Запустите backend
python run.py
```

**Вывод должен показать:**
```
=== Starting Notion RAG Bot ===
✓ Database initialized successfully
✓ Telegram webhook configured successfully
=== Application startup complete ===
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✓ Проверка:** Откройте http://localhost:8000 в браузере - должен появиться JSON с информацией о сервисе.

**⚠️ Если ошибки:**
- **Database error**: Проверьте `DATABASE_URL`
- **Telegram error**: Проверьте `TELEGRAM_BOT_TOKEN`
- **Notion error**: Проверьте `NOTION_TOKEN`

**Не закрывайте этот терминал!**

## 📝 Шаг 4: Инициализация БД

**Откройте НОВЫЙ терминал:**

```bash
cd notiontgLLM

# Инициализируйте БД
curl -X POST "http://localhost:8000/api/v1/admin/db-init?secret=my-super-secret-webhook-path-2024"
```

**Замените** `my-super-secret-webhook-path-2024` на ваш `WEBHOOK_SECRET_PATH`.

**Ожидаемый ответ:**
```json
{
  "status": "ok",
  "message": "Extensions ensured and tables created"
}
```

**✓ Проверка:** Команда вернула status: "ok".

## 📝 Шаг 5: Синхронизация Notion

```bash
# Синхронизируйте Notion данные
curl -X POST "http://localhost:8000/api/v1/admin/ingest?secret=my-super-secret-webhook-path-2024"
```

**Замените** `my-super-secret-webhook-path-2024` на ваш `WEBHOOK_SECRET_PATH`.

**Ожидаемый ответ:**
```json
{
  "status": "completed",
  "stats": {
    "pages_synced": 5,
    "chunks_created": 123
  }
}
```

**✓ Проверка:** `pages_synced` > 0 и `chunks_created` > 0.

**⚠️ Если pages_synced = 0:**
- Проверьте `NOTION_DATABASE_IDS`
- Убедитесь что интеграция имеет доступ к базе данных
- Проверьте что в базе данных есть страницы

## 📝 Шаг 6: Настройка Frontend

**В том же терминале:**

```bash
# Перейдите в директорию frontend
cd frontend

# Установите зависимости
npm install
```

**Это займет 1-2 минуты.**

```bash
# Создайте .env файл
cp .env.example .env

# Откройте в редакторе
# macOS:
open .env
# Linux:
nano .env
# Windows:
notepad .env
```

**Заполните frontend/.env:**

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://localhost:8000
```

**✓ Проверка:** Файл `frontend/.env` существует.

## 📝 Шаг 7: Запуск Frontend

```bash
# Убедитесь что вы в директории frontend
# Если нет:
cd frontend

# Запустите dev сервер
npm run dev
```

**Вывод должен показать:**
```
   ▲ Next.js 15.1.8
   - Local:        http://localhost:3000

 ✓ Starting...
 ✓ Ready in 2.5s
```

**✓ Проверка:** Откройте http://localhost:3000 - должна появиться Dashboard страница.

**⚠️ Если ошибки компиляции:**
- Проверьте что все зависимости установлены: `npm install`
- Проверьте Node.js версию: `node --version` (должна быть 20+)

**Не закрывайте этот терминал!**

## 📝 Шаг 8: Проверка работы

### 8.1 Проверьте Admin Panel

Откройте http://localhost:3000

**Должны увидеть:**
- ✅ Dashboard с статистикой
- ✅ Количество документов (должно быть > 0)
- ✅ Последние документы из Notion

**Протестируйте навигацию:**
- ✅ Documents - список документов
- ✅ Query Logs - пока пусто (норма)
- ✅ Feedback - пока пусто (норма)

### 8.2 Проверьте Telegram Bot

**Найдите вашего бота:**
1. Откройте Telegram
2. Найдите вашего бота по username
3. Нажмите /start

**Бот должен:**
- ✅ Ответить приветствием
- ✅ Показать инструкции

**Задайте вопрос:**
```
Как развернуть приложение?
```

**Бот должен:**
- ✅ Подумать несколько секунд
- ✅ Дать ответ на основе Notion
- ✅ Показать источники
- ✅ Запросить отзыв (👍/👎)

### 8.3 Проверьте логи

**Вернитесь в Admin Panel:**
- ✅ Query Logs - должен появиться ваш вопрос
- ✅ Видны токены и стоимость

**Оставьте отзыв в Telegram** (👍 или 👎)

**Вернитесь в Admin Panel:**
- ✅ Feedback - должен появиться ваш отзыв

## 📝 Шаг 9: Что дальше?

### ✅ Всё работает!

Поздравляю! Теперь у вас работает:
- 🤖 Telegram bot
- 🔧 Backend API
- 🖥️ Admin Panel

### 📖 Изучите документацию:

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Как пользоваться системой
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Как задеплоить в продакшн
- **[README.md](README.md)** - Полная документация

### 🎨 Кастомизация:

- **Стили**: `frontend/app/globals.css`
- **Промпты**: `app/llm.py`
- **Telegram команды**: `bot/telegram.py`

### 🚀 Деплой в продакшн:

Когда будете готовы - читайте [DEPLOYMENT.md](DEPLOYMENT.md)

## 🆘 Проблемы?

### Backend не запускается

**Проверьте:**
1. Виртуальное окружение активировано
2. Все зависимости установлены: `pip install -r requirements.txt`
3. `.env` файл существует и заполнен
4. PostgreSQL запущен и доступен

**Логи:**
- Смотрите вывод в терминале где запущен `python run.py`
- Ищите красные ERROR сообщения

### Frontend не запускается

**Проверьте:**
1. Node.js установлен: `node --version`
2. Зависимости установлены: `npm install`
3. `.env` файл в `frontend/` существует

**Логи:**
- Смотрите вывод в терминале где запущен `npm run dev`
- Ищите красные ERROR сообщения

### Бот не отвечает

**Проверьте:**
1. Backend запущен
2. Webhook настроен: `curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"`
3. Ваш user ID в `ALLOWED_TELEGRAM_USER_IDS`
4. Данные синхронизированы (Шаг 5)

**Как узнать свой Telegram user ID:**
1. Напишите боту [@userinfobot](https://t.me/userinfobot)
2. Он покажет ваш ID

### Нет документов в Admin Panel

**Решение:**
1. Проверьте что синхронизация прошла успешно (Шаг 5)
2. Если `pages_synced` = 0, проверьте настройки Notion
3. Повторите синхронизацию

### Другие проблемы

1. **Перезапустите backend и frontend**
2. **Проверьте логи** в обоих терминалах
3. **Запустите тест**: `./test_api.sh`
4. **Читайте** [USAGE_GUIDE.md](USAGE_GUIDE.md)

## 📋 Чеклист успешного запуска

Отметьте что выполнено:

- [ ] Backend запущен (терминал 1)
- [ ] Frontend запущен (терминал 2)
- [ ] База данных инициализирована
- [ ] Notion синхронизирован
- [ ] Admin Panel открывается
- [ ] Документы отображаются
- [ ] Telegram bot отвечает
- [ ] Запросы логируются
- [ ] Отзывы работают

**Всё отмечено? Поздравляю!** 🎉

## 🎯 Следующие шаги

1. **Используйте** систему локально
2. **Протестируйте** все функции
3. **Изучите** документацию
4. **Когда готовы** - деплойте: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Полезные команды:**

```bash
# Backend
python run.py                                              # Запуск
curl http://localhost:8000/health                         # Проверка
curl -X POST "http://localhost:8000/api/v1/admin/ingest?secret=YOUR_SECRET"  # Синхронизация

# Frontend  
cd frontend && npm run dev                                # Запуск
curl http://localhost:3000                                # Проверка

# Тестирование
./test_api.sh                                             # Проверка API
```

**Полезные URL:**
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

Удачи! 🚀

