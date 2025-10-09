# 🚀 START HERE - Notion Telegram RAG Bot

Добро пожаловать! Это главная точка входа в проект.

## 📋 Что это?

**Notion Telegram RAG Bot** - это полнофункциональная система для ответа на вопросы через Telegram на основе вашей документации в Notion.

**Состоит из:**
- 🤖 **Telegram Bot** - отвечает на вопросы пользователей
- 🔧 **FastAPI Backend** - обрабатывает запросы, работает с БД
- 🖥️ **Next.js Frontend** - веб-интерфейс для управления и аналитики
- 🗄️ **PostgreSQL + pgvector** - хранит документы и embeddings

## ⚡ Быстрый старт (5 минут)

### 1. Установка

```bash
# Клонируйте репозиторий (если еще не сделали)
git clone <your-repo>
cd notiontgLLM

# Backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Конфигурация

```bash
# Создайте .env в корне проекта
cp .env.example .env

# Создайте .env в frontend
cp frontend/.env.example frontend/.env

# Отредактируйте оба файла с вашими credentials
```

### 3. Запуск

```bash
# Терминал 1: Backend
python run.py

# Терминал 2: Frontend
cd frontend
npm run dev
```

### 4. Инициализация

```bash
# Инициализируйте БД
curl -X POST "http://localhost:8000/api/v1/admin/db-init?secret=YOUR_SECRET"

# Синхронизируйте Notion
curl -X POST "http://localhost:8000/api/v1/admin/ingest?secret=YOUR_SECRET"
```

### 5. Готово! 🎉

- **Admin Panel**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Telegram Bot**: Напишите вашему боту в Telegram

## 📚 Документация

### Для быстрого старта
- ✅ **[FINAL_SETUP.md](FINAL_SETUP.md)** - Пошаговая настройка (начните здесь!)
- ✅ **[frontend/QUICKSTART.md](frontend/QUICKSTART.md)** - Быстрый старт фронтенда

### Для деплоя
- 🚀 **[DEPLOYMENT.md](DEPLOYMENT.md)** - Деплой на Railway + Vercel
- 🔧 **[frontend/README.md](frontend/README.md)** - Документация фронтенда

### Для использования
- 📖 **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Как пользоваться системой
- 📊 **[README.md](README.md)** - Общая документация проекта

### Для тестирования
- 🧪 **[test_api.sh](test_api.sh)** - Скрипт для проверки API

## 🎯 Что делать дальше?

### Если вы впервые запускаете проект:
1. ✅ Прочитайте [FINAL_SETUP.md](FINAL_SETUP.md)
2. ✅ Настройте `.env` файлы
3. ✅ Запустите backend и frontend локально
4. ✅ Инициализируйте БД и синхронизируйте Notion
5. ✅ Протестируйте в Telegram и Admin Panel

### Если готовы к деплою:
1. ✅ Прочитайте [DEPLOYMENT.md](DEPLOYMENT.md)
2. ✅ Задеплойте backend на Railway
3. ✅ Задеплойте frontend на Vercel
4. ✅ Настройте переменные окружения
5. ✅ Проверьте что всё работает

### Если хотите кастомизировать:
1. ✅ Frontend стили: `frontend/app/globals.css`
2. ✅ Backend логика: `app/`
3. ✅ Telegram команды: `bot/telegram.py`
4. ✅ Промпты для LLM: `app/llm.py`

## 🏗️ Структура проекта

```
notiontgLLM/
│
├── 📄 START_HERE.md          ← Вы здесь!
├── 📄 FINAL_SETUP.md         ← Пошаговая настройка
├── 📄 DEPLOYMENT.md          ← Инструкции по деплою
├── 📄 USAGE_GUIDE.md         ← Руководство пользователя
├── 📄 README.md              ← Общая документация
│
├── app/                      # Backend код
│   ├── api.py               # API endpoints
│   ├── crud_api.py          # CRUD operations
│   ├── models.py            # Database models
│   ├── llm.py               # OpenAI integration
│   └── ...
│
├── bot/                      # Telegram bot
│   └── telegram.py          # Bot handlers
│
├── frontend/                 # Next.js admin panel
│   ├── 📄 QUICKSTART.md     ← Быстрый старт фронтенда
│   ├── 📄 README.md         ← Документация фронтенда
│   ├── app/                 # Pages & components
│   ├── lib/                 # Utilities
│   └── types/               # TypeScript types
│
├── .env.example             # Пример конфигурации backend
├── requirements.txt         # Python зависимости
├── main.py                  # FastAPI app
└── run.py                   # Entry point
```

## 🔑 Ключевые файлы

### Backend
- `main.py` - FastAPI приложение
- `run.py` - Точка входа
- `app/api.py` - Основные API endpoints
- `app/crud_api.py` - CRUD операции для admin panel
- `app/models.py` - Модели БД
- `bot/telegram.py` - Telegram bot логика

### Frontend
- `frontend/app/page.tsx` - Главная страница (Dashboard)
- `frontend/app/documents/page.tsx` - Страница документов
- `frontend/app/query-logs/page.tsx` - Страница логов
- `frontend/app/feedback/page.tsx` - Страница отзывов
- `frontend/app/globals.css` - Стили

### Конфигурация
- `.env` - Backend environment variables
- `frontend/.env` - Frontend environment variables
- `vercel.json` - Vercel deployment config

## 🛠️ Основные команды

### Backend
```bash
# Запуск
python run.py

# Запуск с автоперезагрузкой
uvicorn main:app --reload

# Инициализация БД
python init_db.py

# Синхронизация Notion
python sync_notion.py
```

### Frontend
```bash
cd frontend

# Разработка
npm run dev

# Билд
npm run build

# Продакшн
npm start

# Линтинг
npm run lint
```

### Тестирование
```bash
# Тест API
./test_api.sh

# С кастомным URL
./test_api.sh https://your-backend.railway.app your_secret
```

## 🎨 Возможности

### ✅ Уже реализовано

- [x] Telegram bot с RAG
- [x] Векторный поиск (pgvector)
- [x] OpenAI интеграция
- [x] Notion синхронизация
- [x] Admin panel (Next.js)
- [x] CRUD операции
- [x] Отслеживание расходов
- [x] Система отзывов
- [x] Деплой на Railway + Vercel

### 🚧 Можно добавить

- [ ] Аутентификация для admin panel
- [ ] Мультиязычность
- [ ] Голосовые сообщения
- [ ] Аналитические дашборды
- [ ] Экспорт данных
- [ ] Scheduled Notion sync
- [ ] Rate limiting
- [ ] Кэширование ответов

## 🆘 Помощь

### Где искать ответы:

1. **Быстрый старт**: [FINAL_SETUP.md](FINAL_SETUP.md)
2. **Деплой**: [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Использование**: [USAGE_GUIDE.md](USAGE_GUIDE.md)
4. **Фронтенд**: [frontend/README.md](frontend/README.md)
5. **API**: http://localhost:8000/docs

### Типичные проблемы:

**Бот не отвечает:**
- Проверьте webhook: `curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"`
- Проверьте `ALLOWED_TELEGRAM_USER_IDS`

**Admin panel не грузится:**
- Проверьте `NEXT_PUBLIC_API_URL` в `frontend/.env`
- Проверьте CORS в `main.py`

**Нет документов в БД:**
- Синхронизируйте Notion: `curl -X POST "http://localhost:8000/api/v1/admin/ingest?secret=YOUR_SECRET"`

## 📞 Поддержка

1. Проверьте документацию выше
2. Проверьте логи (backend + frontend)
3. Запустите `./test_api.sh` для проверки API
4. Откройте issue на GitHub

## 🎓 Обучающие материалы

- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js**: https://nextjs.org/docs
- **Telegram Bot API**: https://core.telegram.org/bots/api
- **Notion API**: https://developers.notion.com
- **OpenAI API**: https://platform.openai.com/docs
- **pgvector**: https://github.com/pgvector/pgvector

## ⭐ Следующие шаги

### Новичок в проекте:
1. ➡️ Читайте [FINAL_SETUP.md](FINAL_SETUP.md)
2. ➡️ Настройте локальное окружение
3. ➡️ Протестируйте функциональность

### Готовы к деплою:
1. ➡️ Читайте [DEPLOYMENT.md](DEPLOYMENT.md)
2. ➡️ Деплойте на Railway + Vercel
3. ➡️ Настройте мониторинг

### Хотите кастомизировать:
1. ➡️ Изучите структуру проекта
2. ➡️ Внесите изменения
3. ➡️ Протестируйте
4. ➡️ Задеплойте

---

## 🎉 Удачи!

Проект готов к использованию. Если возникнут вопросы - документация выше поможет вам.

**Созданные документы:**
- ✅ START_HERE.md (этот файл)
- ✅ FINAL_SETUP.md (пошаговая настройка)
- ✅ DEPLOYMENT.md (инструкции по деплою)
- ✅ USAGE_GUIDE.md (руководство пользователя)
- ✅ README.md (общая документация)
- ✅ frontend/README.md (документация фронтенда)
- ✅ frontend/QUICKSTART.md (быстрый старт фронтенда)

**Полезные команды:**
```bash
# Локальный запуск
python run.py                    # Backend
cd frontend && npm run dev       # Frontend

# Тестирование
./test_api.sh                    # Проверка API

# Инициализация
curl -X POST "http://localhost:8000/api/v1/admin/db-init?secret=YOUR_SECRET"
curl -X POST "http://localhost:8000/api/v1/admin/ingest?secret=YOUR_SECRET"
```

**Полезные ссылки:**
- 🌐 Frontend: http://localhost:3000
- 🔧 API Docs: http://localhost:8000/docs
- 📊 Health: http://localhost:8000/health

Начните с [FINAL_SETUP.md](FINAL_SETUP.md)! 🚀

