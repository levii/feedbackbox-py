import copy
import datetime
import pickle
import typing
import sys
import os

from injector import inject
from models import Feedback
from infra import Repository
from infra import Store

DATABASE_FILE = "datafile.pickle"


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
