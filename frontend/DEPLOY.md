# Деплой на Vercel

## Быстрый деплой

### 1. Через Vercel Dashboard

1. Залейте код на GitHub:
```bash
git push
```

2. Импортируйте в Vercel:
   - Перейдите на [vercel.com](https://vercel.com)
   - New Project → Import your repository
   - **Root Directory**: `frontend`

3. Настройте переменные окружения:
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
API_URL=https://your-backend.railway.app
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

4. Deploy!

### 2. Через CLI

```bash
cd frontend
vercel login
vercel

# Добавьте переменные
vercel env add NEXT_PUBLIC_API_URL
vercel env add API_URL  
vercel env add ADMIN_USERNAME
vercel env add ADMIN_PASSWORD

# Production deploy
vercel --prod
```

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `NEXT_PUBLIC_API_URL` | Backend URL (клиент) | `https://api.yourdomain.com` |
| `API_URL` | Backend URL (сервер) | `https://api.yourdomain.com` |
| `ADMIN_USERNAME` | Логин админа | `admin` |
| `ADMIN_PASSWORD` | Пароль админа | `your_secure_password` |

## Аутентификация

- Логин: значение из `ADMIN_USERNAME`
- Пароль: значение из `ADMIN_PASSWORD`
- Cookie хранится 7 дней

## После деплоя

1. Откройте ваш Vercel URL
2. Войдите с учетными данными
3. Проверьте что все работает

## CORS на бекенде

Убедитесь что бекенд разрешает запросы с вашего Vercel домена:

```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Готово! 🎉

Ваш админ-панель доступен по адресу Vercel.

