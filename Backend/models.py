from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    id: Optional[str] = None
    title: str
    is_done: bool = False
