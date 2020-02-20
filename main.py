import typing
import sys
import os

from injector import Injector
from injector import singleton
from handlers import FeedbackCreateHandler
from handlers import FeedbackFetchListHandler

from infra import Response
from infra import Repository

DATABASE_FILE = "datafile.pickle"


def main(argv: typing.List[str], injector: typing.Optional[Injector] = None) -> Response:
    if injector is None:
        injector = Injector()

    if len(argv) <= 1:
        progname = os.path.basename(argv[0]) if len(argv) > 0 else "<progname>"
        return Response(mode="", status=500, message=[f"[usage] {progname} <mode>"])

    mode = argv[1]
    if mode == "create-feedback":
        create_handler: FeedbackCreateHandler = injector.get(FeedbackCreateHandler)
        feedback = create_handler.execute(title="要望タイトル", description="要望本文")
        return Response(mode=mode, status=200, message=[feedback])
    elif mode == "list-feedbacks":
        fetch_list_handler: FeedbackFetchListHandler = injector.get(FeedbackFetchListHandler)
        feedbacks = fetch_list_handler.execute()
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
