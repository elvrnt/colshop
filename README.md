# MVP: Сервис коллективных покупок

Стек: Python 3.12, Django 5, DRF, Graphene, PostgreSQL (по умолчанию SQLite для локального запуска).

## Запуск локально
1. Создать окружение и поставить зависимости:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
2. Применить миграции и создать суперпользователя (опционально для админки):
   ```bash
   .venv\Scripts\python manage.py migrate
   .venv\Scripts\python manage.py createsuperuser
   ```
3. Запустить dev-сервер:
   ```bash
   .venv\Scripts\python manage.py runserver
   ```

## Основные сущности
- `Product` — товар/предложение.
- `Campaign` — кампания коллективной покупки, статус, дедлайн, правила цен.
- `Participation` — участие пользователя, количество, сумма.
- `PaymentIntent` — заглушка платежа (идемпотентный ключ, статус).
- `Notification` — очередь уведомлений (канал, шаблон, статус).

## REST API (DRF)
Базовый префикс: `/api/rest/`
- Аутентификация: `POST /auth/register`, `POST /auth/login` (Token), `GET /me`.
- CRUD: `products`, `campaigns`, `participations` (только свои), `payments`.
- Действие: `POST /campaigns/{id}/join` — вступление в кампанию (quantity).

## GraphQL
- Endpoint: `/api/graphql` (GraphiQL включён).
- Запросы: `products`, `campaigns(status)`, `participations` (только свои).

## Мини-фронтенд
Статичная страница `http://localhost:8000/`:
- Регистрация/логин (Token), создание продуктов и кампаний, вступление в кампанию.
- Данные подтягиваются из REST API.

## Настройки БД
По умолчанию SQLite. Для PostgreSQL задайте переменные окружения:
`DB_ENGINE=django.db.backends.postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

## Следующие шаги
- Добавить реальный платёжный провайдер и вебхуки.
- Вынести очереди/уведомления на Celery/Redis.
- Подключить JWT/OAuth2, rate limiting, и API Gateway (nginx/Traefik/Kong).

