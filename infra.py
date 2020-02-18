import dataclasses
import datetime
import os
import pickle

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from models import Feedback


@dataclasses.dataclass()
class Store:
    feedbacks: List[Feedback] = dataclasses.field(default_factory=list)
    created_at: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.utcnow)


@dataclasses.dataclass()
class Repository:
    store: Store = dataclasses.field(default_factory=Store)
    filename: Optional[str] = None

    def reset(self):
        self.store = Store()

    @classmethod
    def load(cls, filename: str) -> "Repository":
        if os.path.exists(filename):
            with open(filename, "rb") as file:
                store = pickle.load(file)
        else:
            store = Store()
        return cls(
            store=store,
            filename=filename
        )

    def persistent(self):
        if self.filename is None:
            return

        with open(self.filename, "wb") as file:
            pickle.dump(self.store, file)


@dataclasses.dataclass()
class Response:
    mode: str
    status: int
    message: Union[List[Any], Dict[Any, Any]]
