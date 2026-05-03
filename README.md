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