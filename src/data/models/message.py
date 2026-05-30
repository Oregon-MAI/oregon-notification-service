import uuid


class Message:
    """
    Модель уведомления с идентификатором, текстом и ID пользователя
    """

    id: uuid.UUID
    text: str
    user_id: uuid.UUID

    def __init__(self, id: uuid.UUID, text: str, user_id: uuid.UUID) -> None:
        """
        Инициализирует объект сообщения
        :return: None
        """
        self.id = id
        self.text = text
        self.user_id = user_id

    def to_dict(self) -> dict[str, str]:
        """
        Преобразует сообщение в словарь для сериализации
        :return: dict с полями id, text, user_id в строковом формате
        """
        return {"id": str(self.id), "text": str(self.text), "user_id": str(self.user_id)}

    @classmethod
    def from_dict(cls, data: dict) -> Message:
        """
        Создаёт объект Message из словаря
        :return: новый экземпляр Message
        """
        return cls(id=uuid.UUID(data["id"]), text=data["text"], user_id=uuid.UUID(data["user_id"]))
