import dataclasses
import datetime


@dataclasses.dataclass(frozen=True)
class Feedback:
    feedback_id: str
    title: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
