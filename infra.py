import dataclasses
import datetime
import os
import pickle
import typing

from models import Feedback


@dataclasses.dataclass()
class Store:
    feedbacks: typing.List[Feedback] = dataclasses.field(default_factory=list)
    created_at: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.utcnow)


@dataclasses.dataclass()
class Repository:
    store: Store = dataclasses.field(default_factory=Store)
    filename: typing.Optional[str] = None

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
