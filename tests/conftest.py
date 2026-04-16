import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

sys.modules["src.repositories.message_repository"] = MagicMock()
sys.modules["src.repositories.message_repository"].get_messages_by_user_id = AsyncMock(
    return_value=[]
)
sys.modules["src.repositories.message_repository"].delete_messages_by_user_id = AsyncMock(
    return_value=None
)
sys.modules["src.repositories.message_repository"].engine = MagicMock()

root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
