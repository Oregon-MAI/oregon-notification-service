import uuid
from uuid import uuid4

from sqlalchemy import UUID, Column, Text

from src.data.models.base import Base


class Message(Base):
    __tablename__ = "tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    text = Column(Text, index=True, nullable=False)
    user_id = Column(UUID, nullable=False)

    def __init__(self, id: uuid.UUID, text: str, user_id: uuid.UUID) -> None:
        self.id = id
        self.text = text
        self.user_id = user_id
