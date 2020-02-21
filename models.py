import dataclasses
import datetime
from typing import List
from typing import Optional


@dataclasses.dataclass(frozen=False)
class FeedbackComment:
    user_id: int
    body: str
    created_at: datetime.datetime


@dataclasses.dataclass(frozen=True)
class Feedback:
    feedback_id: str
    user_id: int
    title: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    comments: List[FeedbackComment] = dataclasses.field(default_factory=list)


@dataclasses.dataclass(frozen=False)
class User:
    name: str
    role: str
    user_id: Optional[int] = None
