import argparse
import sys
import typing

from injector import Injector
from injector import singleton
from handlers import FeedbackCreateHandler
from handlers import FeedbackFetchListHandler

from infra import Response
from infra import Repository
from models import User

DATABASE_FILE = "datafile.pickle"


def build_parser():
    parser = argparse.ArgumentParser(prog="FeedbackBox")
    subparsers = parser.add_subparsers()

    parser_feedback = subparsers.add_parser("feedback")
    feedback_subparsers = parser_feedback.add_subparsers()

    feedback_create_parser = feedback_subparsers.add_parser("create")
    feedback_create_parser.add_argument("--title", type=str, help="Title", required=True)
    feedback_create_parser.add_argument("--description", type=str, help="Description", required=True)
    feedback_create_parser.add_argument("--user_id", type=int, help="UserID", required=True)
    feedback_create_parser.set_defaults(mode="feedback-create")

    feedback_list_parser = feedback_subparsers.add_parser("list")
    feedback_list_parser.add_argument("--user_id", type=int, help="UserID", required=True)
    feedback_list_parser.set_defaults(mode="feedback-list")

    return parser


def main(mode: str, args: argparse.Namespace, injector: typing.Optional[Injector] = None) -> Response:
    if injector is None:
        injector = Injector()

    if mode == "feedback-create":
        create_handler: FeedbackCreateHandler = injector.get(FeedbackCreateHandler)
        feedback = create_handler.execute(title=args.title, description=args.description, user_id=args.user_id)
        return Response(mode=mode, status=200, message=[feedback])
    elif mode == "feedback-list":
        user = User(name="Test User", role="support", user_id=1)
        fetch_list_handler: FeedbackFetchListHandler = injector.get(FeedbackFetchListHandler)
        feedbacks = fetch_list_handler.execute(user=user)
        return Response(mode=mode, status=200, message=feedbacks)
    else:
        raise RuntimeError(f"Unknown mode: {mode}")


if __name__ == "__main__":
    arg_parser = build_parser()
    options = arg_parser.parse_args()

    if "mode" not in options:
        arg_parser.parse_args(sys.argv[1:] + ["-h"])
        exit()

    container = Injector()
    repository = Repository.load(filename=DATABASE_FILE)
    container.binder.bind(Repository, to=repository, scope=singleton)

    response = main(mode=options.mode, args=options, injector=container)
    print(response.pretty())

    repository.persistent()
