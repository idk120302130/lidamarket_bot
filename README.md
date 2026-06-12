# Telegram Mini App с обучением и геймификацией

Полноценное приложение с React-фронтендом, aiohttp API, и базой PostgreSQL.

## Локальный запуск (Docker)

Для самого простого запуска всего проекта используйте Docker:

1. Переименуйте `.env.example` в `.env` и укажите свой `BOT_TOKEN` и `ADMIN_IDS`.
2. Выполните команду сборки и запуска:
   ```bash
   docker-compose up --build
   ```

## Развертывание на Railway

Railway отлично подходит для развертывания подобных проектов благодаря встроенной поддержке Dockerfile.

1. Создайте проект в Railway.
2. Подключите ваш GitHub репозиторий.
3. Добавьте базы данных: **PostgreSQL** и **Redis** прямо в Railway (New -> Database).
4. Укажите переменные окружения (Environment Variables) для основного сервиса:
   - `BOT_TOKEN`: ваш токен
   - `DATABASE_URL`: `postgresql+asyncpg://...` (скопируйте из настроек Postgres на Railway, замените postgresql:// на postgresql+asyncpg://)
   - `REDIS_URL`: URL от Redis
   - `ADMIN_IDS`: ваш ID
   - `PAYMENT_TEXT_RU`, `PAYMENT_TEXT_BY`
   - `WEBAPP_URL`: публичный домен приложения на Railway (например, `https://myapp.up.railway.app`)
5. Настройте порт: Railway автоматически прокидывает переменную `PORT`. Вы можете использовать её или оставить `8000`. Убедитесь, что в Railway Custom Domain направлен на порт бота (8000 по умолчанию).
6. Деплой пройдет автоматически.
