import uuid


class Message:
    id: uuid.UUID
    text: str
    user_id: uuid.UUID

    def __init__(self, id: uuid.UUID, text: str, user_id: uuid.UUID) -> None:
        self.id = id
        self.text = text
        self.user_id = user_id

    def to_dict(self) -> dict[str, str]:
        return {
            "id": str(self.id),
            "text": str(self.text),
            "user_id": str(self.user_id)
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=uuid.UUID(data["id"]),
            text=data["text"],
            user_id=uuid.UUID(data["user_id"])
        )
