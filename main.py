import dataclasses
import datetime
import pickle
import typing
import sys
import os

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
