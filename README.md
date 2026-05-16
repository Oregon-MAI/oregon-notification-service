# oregon-notification-service

### Эндпоинты

1. GET /notifications/{user_id} 
    Устанавливает SSE-соединение. Отправляет уведомдения реальном времени.
2. POST /notifications/confirm/{user_id}/{message_id}
    Подтверждает прочтение пользователем уведомления.

### Структура

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
Также в репозитории находятся 4 юнит теста, обеспечивающие покрытие >80%.

## Что требуется для запуска

1. Необходимо собрать образ приложения при помощи команды docker build.
2. Написать docker-compose.yaml или запустить compose файл, лежащий в репозитории, содержащий  PostgreSQL, redis, confluentinc/cp-kafka, confluentinc/cp-zookeeper .
3. Необходимо создать 6 топиков в kafka: USER_BOOK_TOPIC, USER_CANCEL_TOPIC, ADMIN_CANCEL_TOPIC, ADMIN_UPDATE_TOPIC,MESSAGES_TOPIC_START,MESSAGES_TOPIC_END.
4. Добавить переменные окружения для сервиса уведомлений: EDIS_PASS,REDIS_URL,KAFKA_BOOTSTRAP_SERVERS,USER_BOOK_TOPIC,USER_CANCEL_TOPIC,ADMIN_CANCEL_TOPIC,ADMIN_CANCEL_TOPIC,ADMIN_UPDATE_TOPIC,MESSAGES_TOPIC_START,MESSAGES_TOPIC_END,DATABASE_URL.
5. Запустить compose файл и начать наслаждаться сервисом уведомлений.