import copy
import datetime
import typing
import sys
import os

from injector import Injector
from injector import inject
from injector import singleton

from infra import Response
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


class FeedbackCreateService:
    @inject
    def __init__(self, feedback_repository: FeedbackRepository):
        self._feedback_repository = feedback_repository

    def execute(self, title: str, description: str) -> Feedback:
        now = datetime.datetime.utcnow()
        feedback = Feedback(
            feedback_id=int(datetime.datetime.utcnow().timestamp()),
            title=title,
            description=description,
            created_at=now,
            updated_at=now,
        )
        self._feedback_repository.save(feedback=feedback)
        return feedback


class FeedbackFetchListService:
    @inject
    def __init__(self, feedback_repository: FeedbackRepository):
        self._feedback_repository = feedback_repository

    def execute(self) -> typing.List[Feedback]:
        return self._feedback_repository.fetch_list()


def main(argv: typing.List[str], injector: typing.Optional[Injector] = None) -> Response:
    if injector is None:
        injector = Injector()

    if len(argv) <= 1:
        progname = os.path.basename(argv[0]) if len(argv) > 0 else "<progname>"
        return Response(mode="", status=500, message=[f"[usage] {progname} <mode>"])

    mode = argv[1]
    if mode == "create-feedback":
        create_service: FeedbackCreateService = injector.get(FeedbackCreateService)
        feedback = create_service.execute(title="要望タイトル", description="要望本文")
        return Response(mode=mode, status=200, message=[feedback])
    elif mode == "list-feedbacks":
        fetch_list_service: FeedbackFetchListService = injector.get(FeedbackFetchListService)
        feedbacks = fetch_list_service.execute()
        return Response(mode=mode, status=200, message=feedbacks)
    else:
        raise RuntimeError(f"Unknown mode: {mode}")


if __name__ == "__main__":
    container = Injector()
    repository = Repository.load(filename=DATABASE_FILE)
    container.binder.bind(Repository, to=repository, scope=singleton)

    response = main(argv=sys.argv, injector=container)
    print(response)

    repository.persistent()
