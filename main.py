import copy
import dataclasses
import datetime
import pickle
import typing
import sys
import os

from injector import inject

DATABASE_FILE = "datafile.pickle"


@dataclasses.dataclass(frozen=True)
class Feedback:
    feedback_id: int
    title: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


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
        with open(self.filename, "wb") as file:
            pickle.dump(self.store, file)


class FeedbackRepository:
    @inject
    def __init__(self, repository: Repository):
        self._repository = repository

    @property
    def _store(self) -> Store:
        return self._repository.store

    def save(self, feedback: Feedback):
        self._store.feedbacks.append(feedback)

    def fetch_list(self) -> typing.List[Feedback]:
        return copy.deepcopy(self._store.feedbacks)


def create_feedback() -> Feedback:
    now = datetime.datetime.utcnow()
    feedback = Feedback(
        feedback_id=int(datetime.datetime.utcnow().timestamp()),
        title="要望のタイトル",
        description="要望の本文",
        created_at=now,
        updated_at=now,
    )
    return feedback


def list_feedbacks(store: Store) -> None:
    print("===== Feedback =====")
    for feedback in store.feedbacks:
        print(feedback)


def main(argv: typing.List[str], database_file: typing.Optional[str] = None) -> typing.Optional[int]:
    if database_file is None:
        database_file = DATABASE_FILE

    if os.path.exists(database_file):
        with open(database_file, "rb") as file:
            store = pickle.load(file)
    else:
        store = Store()

    if len(argv) <= 1:
        progname = os.path.basename(argv[0]) if len(argv) > 0 else "<progname>"
        print(f"[Usage] {progname} <mode>")
        return None

    mode = argv[1]
    if mode == "create-feedback":
        feedback = create_feedback()
        store.feedbacks.append(feedback)
    elif mode == "list-feedbacks":
        list_feedbacks(store)
    else:
        raise RuntimeError(f"Unknown mode: {mode}")

    with open(database_file, "wb") as file:
        pickle.dump(store, file)


if __name__ == "__main__":
    main(argv=sys.argv)
