import os

REDIS_PASS = os.getenv("REDIS_PASS", "")
REDIS_URL = os.getenv("REDIS_URL", "")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
USER_BOOK_TOPIC = os.getenv("USER_BOOK_TOPIC", "")
USER_CANCEL_TOPIC = os.getenv("USER_CANCEL_TOPIC", "")
ADMIN_CANCEL_TOPIC = os.getenv("ADMIN_CANCEL_TOPIC", "")
ADMIN_UPDATE_TOPIC = os.getenv("ADMIN_UPDATE_TOPIC", "")
MESSAGES_TOPIC_START = os.getenv("MESSAGES_TOPIC_START", "")
MESSAGES_TOPIC_END = os.getenv("MESSAGES_TOPIC_END", "")
CONSUME_TOPICS = [
    USER_BOOK_TOPIC,
    USER_CANCEL_TOPIC,
    ADMIN_CANCEL_TOPIC,
    ADMIN_UPDATE_TOPIC,
    MESSAGES_TOPIC_START,
    MESSAGES_TOPIC_END,
]
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
KAFKA_GROUP_ID = "notification"
DB_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
MONTHS = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]
