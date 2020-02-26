import argparse
import sys
import typing

from injector import Injector
from injector import singleton

from handlers import FeedbackCommentCreateHandler
from handlers import FeedbackCreateHandler
from handlers import FeedbackFetchHandler
from handlers import FeedbackFetchListHandler
from handlers import FeedbackUpdateHandler
from handlers import UserCreateHandler
from handlers import UserRepository

from infra import Response
from infra import Repository

DATABASE_FILE = "datafile.pickle"


def build_parser():
    parser = argparse.ArgumentParser(prog="FeedbackBox")
    subparsers = parser.add_subparsers()

    parser_user = subparsers.add_parser("user")
    user_subparsers = parser_user.add_subparsers()

    user_create_parser = user_subparsers.add_parser("create")
    user_create_parser.add_argument("--name", type=str, help="UserName", required=True)
    user_create_parser.add_argument("--role", type=str, help="Role (customer, support)", required=True)
    user_create_parser.add_argument("--user_id", type=int, help="UserID (optional)", required=False)
    user_create_parser.set_defaults(mode="user-create")

    user_list_parser = user_subparsers.add_parser("list")
    user_list_parser.set_defaults(mode="user-list")

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

    feedback_show_parser = feedback_subparsers.add_parser("show")
    feedback_show_parser.add_argument("--user_id", type=int, help="UserID", required=True)
    feedback_show_parser.add_argument("--feedback_id", type=str, help="Feedback ID", required=True)
    feedback_show_parser.set_defaults(mode="feedback-show")

    feedback_update_parser = feedback_subparsers.add_parser("update")
    feedback_update_parser.add_argument("--feedback_id", type=str, help="Feedback ID", required=True)
    feedback_update_parser.add_argument("--user_id", type=int, help="UserID", required=True)
    feedback_update_parser.add_argument("--status", type=str, help="New status", required=False)
    feedback_update_parser.add_argument("--support_comment", type=str, help="Support Comment", required=False)
    feedback_update_parser.set_defaults(mode="feedback-update")

    feedback_comment_parser = feedback_subparsers.add_parser("comment")
    feedback_comment_subparsers = feedback_comment_parser.add_subparsers()

    feedback_comment_create_parser = feedback_comment_subparsers.add_parser("create")
    feedback_comment_create_parser.add_argument("--feedback_id", type=str, help="Feedback ID", required=True)
    feedback_comment_create_parser.add_argument("--comment", type=str, help="Comment Body", required=True)
    feedback_comment_create_parser.add_argument("--user_id", type=int, help="Comment User ID", required=True)
    feedback_comment_create_parser.set_defaults(mode="feedback-comment-create")

    return parser


def main(mode: str, args: argparse.Namespace, injector: typing.Optional[Injector] = None) -> Response:
    if injector is None:
        injector = Injector()

    if mode == "user-create":
        user_create_handler: UserCreateHandler = injector.get(UserCreateHandler)
        user = user_create_handler.execute(name=args.name, role=args.role, user_id=args.user_id)
        return Response(mode=mode, status=200, message=[user])
    elif mode == "user-list":
        user_repository: UserRepository = injector.get(UserRepository)
        users = user_repository.fetch_list()
        return Response(mode=mode, status=200, message=users)
    elif mode == "feedback-create":
        create_handler: FeedbackCreateHandler = injector.get(FeedbackCreateHandler)
        feedback = create_handler.execute(title=args.title, description=args.description, user_id=args.user_id)
        return Response(mode=mode, status=200, message=[feedback])
    elif mode == "feedback-list":
        fetch_list_handler: FeedbackFetchListHandler = injector.get(FeedbackFetchListHandler)
        feedbacks = fetch_list_handler.execute(user_id=args.user_id)
        return Response(mode=mode, status=200, message=feedbacks)
    elif mode == "feedback-show":
        fetch_handler: FeedbackFetchHandler = injector.get(FeedbackFetchHandler)
        feedback = fetch_handler.execute(user_id=args.user_id, feedback_id=args.feedback_id)
        message = [feedback, "", "comments:"]
        message.extend(feedback.comments)
        return Response(mode=mode, status=200, message=message)
    elif mode == "feedback-update":
        feedback_update_handler: FeedbackUpdateHandler = injector.get(
            FeedbackUpdateHandler
        )
        feedback = feedback_update_handler.execute(
            user_id=args.user_id,
            feedback_id=args.feedback_id,
            status=args.status,
            support_comment=args.support_comment,
        )
        return Response(mode=mode, status=200, message=[feedback])
    elif mode == "feedback-comment-create":
        feedback_comment_handler: FeedbackCommentCreateHandler = injector.get(FeedbackCommentCreateHandler)
        comment = feedback_comment_handler.execute(user_id=args.user_id, feedback_id=args.feedback_id, body=args.comment)
        return Response(mode=mode, status=200, message=[comment])
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
