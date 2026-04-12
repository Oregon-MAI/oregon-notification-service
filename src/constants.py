import os

CONSUME_TOPICS = [t for t in os.getenv("TOPICS", "").split(",") if t!='']
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_GROUP_ID = 'notification'