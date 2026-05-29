# Notification Service

Сервис уведомлений в реальном времени. Предоставляет доставку событий пользователям через Server-Sent Events, потребляет сообщения из Kafka, обеспечивает идемпотентность и подтверждение прочтения.

## Возможности

- Real-time уведомления через Server-Sent Events
- Потребление Kafka: обработка событий: бронирования, отмены, обновления, напоминания
- Два уровня хранения: Redis для кэша сообщений пользователя, PostgreSQL для трекинга отправленных
- Подтверждение прочтения
- Структурированное логирование: вывод в файл notification.log

## Технологический стек

- Язык: Python 3.14 
- Фреймворк: FastAPI
- База данных: PostgreSQL 
- ORM: SQLAlchemy 2.0
- Кэш: Redis 
- Message Broker: Kafka
- Контейнеризация: Docker, Docker Compose

## Быстрый старт

Запуск через Docker Compose:

docker compose up

Сервис доступен по адресу: http://localhost:8003

Для запуска требуются запущенные экземпляры: PostgreSQL, Redis, Kafka+Zookeeper.

## Переменные окружения

Основные переменные:

DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db Строка подключения к PostgreSQL

REDIS_URL=redis Хост Redis

REDIS_PORT=6379 Порт Redis

REDIS_PASS=redispass Пароль Redis

KAFKA_BOOTSTRAP_SERVERS=kafka:29092 Адрес Kafka broker

USER_BOOK_TOPIC=user.book Топик успешных бронирований

USER_CANCEL_TOPIC=user.cancel Топик отмен пользователем

ADMIN_CANCEL_TOPIC=admin.cancel Топик отмен администратором

ADMIN_UPDATE_TOPIC=admin.update Топик обновлений администратором

MESSAGES_TOPIC_START=messages.start Напоминание за 15 мин до начала

MESSAGES_TOPIC_END=messages.end Напоминание за 15 мин до окончания

## API

GET /notifications/{user_id} Устанавливает SSE-соединение, отправляет историю + новые уведомления в реальном времени Ответ: text/event-stream

Подтверждение прочтения:

POST /notifications/confirm/{user_id}/{message_id} Помечает уведомление как прочитанное. Ответ: "success" или 404

## Сценарии использования

Получение уведомления в реальном времени:

1. Клиент открывает соединение: GET /notifications/{user_id}
2. Сервис загружает историю из Redis и отправляет через SSE
3. При поступлении нового события из Kafka:
   - Парсится сообщение согласно типу топика
   - Проверяется хеш в PostgreSQL
   - Сохраняется в Redis и отправляется клиенту
4. Клиент отображает уведомление пользователю

## Структура проекта

```
<pre>
    ├── api/
    │   └── routers/
            ├── notification_router.py 
    ├── consumers/
            ├── consumer.py 
    ├── data/
    │   └── models/   
            ├── message.py 
    ├── repositories/
            ├── message_repository.py 
    ├── services/
    │   ├── background_service.py  
    │   ├── connection_service.py  
    │   └── messages_service.py   
    ├── constants.py 
    └── main.py               
</pre>
```
