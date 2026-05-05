import uuid
from uuid import uuid4

from sqlalchemy import UUID, Column, Text

from src.data.models.base import Base


class Send(Base):
    __tablename__ = "sends"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    hash = Column(Text, index=True, nullable=False)

    def __init__(self, id: uuid.UUID, hash: str) -> None:
        self.id = id
        self.hash = hash
