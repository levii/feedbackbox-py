import dataclasses
import datetime
from typing import Optional


@dataclasses.dataclass(frozen=True)
class Feedback:
    feedback_id: str
    title: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclasses.dataclass(frozen=False)
class User:
    name: str
    role: str
    user_id: Optional[int] = None
