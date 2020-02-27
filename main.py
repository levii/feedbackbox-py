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
    sps = parser.add_subparsers()

    pu = sps.add_parser("user")
    us = pu.add_subparsers()

    ucp = us.add_parser("create")
    ucp.add_argument("--name", type=str, help="UserName", required=True)
    ucp.add_argument("--role", type=str, help="Role (customer, support)", required=True)
    ucp.add_argument("--user_id", type=int, help="UserID (optional)", required=False)
    ucp.set_defaults(mode="user-create")

    ulp = us.add_parser("list")
    ulp.set_defaults(mode="user-list")

    pf = sps.add_parser("feedback")
    fs = pf.add_subparsers()

    fcp = fs.add_parser("create")
    fcp.add_argument("--title", type=str, help="Title", required=True)
    fcp.add_argument("--description", type=str, help="Description", required=True)
    fcp.add_argument("--user_id", type=int, help="UserID", required=True)
    fcp.set_defaults(mode="feedback-create")

    flp = fs.add_parser("list")
    flp.add_argument("--user_id", type=int, help="UserID", required=True)
    flp.add_argument("--recently", type=bool, help="Recently filter", required=False)
    flp.set_defaults(mode="feedback-list")

    fsp = fs.add_parser("show")
    fsp.add_argument("--user_id", type=int, help="UserID", required=True)
    fsp.add_argument("--feedback_id", type=str, help="Feedback ID", required=True)
    fsp.set_defaults(mode="feedback-show")

    fup = fs.add_parser("update")
    fup.add_argument("--feedback_id", type=str, help="Feedback ID", required=True)
    fup.add_argument("--user_id", type=int, help="UserID", required=True)
    fup.add_argument("--status", type=str, help="New status", required=False)
    fup.add_argument("--support_comment", type=str, help="Support Comment", required=False)
    fup.set_defaults(mode="feedback-update")

    fcp = fs.add_parser("comment")
    fcs = fcp.add_subparsers()

    fccp = fcs.add_parser("create")
    fccp.add_argument("--feedback_id", type=str, help="Feedback ID", required=True)
    fccp.add_argument("--comment", type=str, help="Comment Body", required=True)
    fccp.add_argument("--user_id", type=int, help="Comment User ID", required=True)
    fccp.set_defaults(mode="feedback-comment-create")

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
        feedbacks = fetch_list_handler.execute(user_id=args.user_id, recently=args.recently)
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
