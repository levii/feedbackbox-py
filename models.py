import dataclasses
import datetime
from typing import List
from typing import Optional

import injector


@dataclasses.dataclass(frozen=False)
class FeedbackComment:
    user_id: int
    body: str
    created_at: datetime.datetime

    def is_by_support(self) -> bool:
        from handlers import UserRepository

        user_repository: UserRepository = injector.get(UserRepository)
        user = user_repository.fetch(self.user_id)
        return user.role == "support"


@dataclasses.dataclass(frozen=True)
class Feedback:
    feedback_id: str
    user_id: int
    title: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    comments: List[FeedbackComment] = dataclasses.field(default_factory=list)
    status: str = "new"
    support_comment: Optional[str] = None

    def modify(self, **changes) -> "Feedback":
        return dataclasses.replace(self, **changes)

    def is_latest_comment_by_support(self) -> bool:
        if len(self.comments) == 0:
            return False

        latest_comment = self.comments[-1]
        return latest_comment.is_by_support()


@dataclasses.dataclass(frozen=False)
class User:
    name: str
    role: str
    user_id: Optional[int] = None
