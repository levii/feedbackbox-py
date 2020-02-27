import copy
import dataclasses
import datetime
import typing
import uuid

from injector import inject

from infra import Repository
from infra import Store
from models import Feedback
from models import FeedbackComment
from models import User


class UserRepository:
    @inject
    def __init__(self, repository: Repository):
        self._repository = repository

    @property
    def _store(self) -> Store:
        return self._repository.store

    def save(self, user: User) -> User:
        if user.user_id is None:
            user.user_id = self._store.next_user_id
            self._store.next_user_id += 1

        self._store.users[user.user_id] = user
        return user

    def fetch(self, user_id: int) -> typing.Optional[User]:
        return self._store.users.get(user_id)

    def fetch_list(self) -> typing.List[User]:
        users = []
        for user in self._store.users.values():
            users.append(user)
        return users


class UserCreateHandler:
    @inject
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def execute(self, name: str, role: str, user_id: typing.Optional[int]) -> User:
        user = User(name, role, user_id=user_id)
        self._user_repository.save(user)
        return user


class FeedbackRepository:
    @inject
    def __init__(self, repository: Repository):
        self._repository = repository

    @property
    def _store(self) -> Store:
        return self._repository.store

    def save(self, feedback: Feedback):
        for i in reversed(range(len(self._store.feedbacks))):
            if self._store.feedbacks[i].feedback_id == feedback.feedback_id:
                del self._store.feedbacks[i]

        self._store.feedbacks.append(feedback)

    def fetch_list(self) -> typing.List[Feedback]:
        return copy.deepcopy(self._store.feedbacks)


class FeedbackCreateHandler:
    @inject
    def __init__(self, feedback_repository: FeedbackRepository):
        self._feedback_repository = feedback_repository

    def execute(self, title: str, description: str, user_id: int) -> Feedback:
        now = datetime.datetime.utcnow()
        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            created_at=now,
            updated_at=now,
        )
        self._feedback_repository.save(feedback=feedback)
        return feedback


@dataclasses.dataclass
class FeedbackCollection:
    collection: typing.List[Feedback]

    def filter_by_user_id(self, user_id: int) -> "FeedbackCollection":
        result = []
        for feedback in self.collection:
            if feedback.user_id == user_id:
                result.append(feedback)
        return self.__class__(result)

    def filter_latest_comment_by_other_user(self, user_id: int) -> "FeedbackCollection":
        pass

    def __iter__(self):
        return self.collection.__iter__()


class FeedbackFetchListHandler:
    @inject
    def __init__(
        self, user_repository: UserRepository, feedback_repository: FeedbackRepository
    ):
        self._user_repository = user_repository
        self._feedback_repository = feedback_repository

    def execute(self, user_id: int, recently: bool) -> typing.List[Feedback]:
        user = self._user_repository.fetch(user_id)
        if user is None:
            raise RuntimeError(f"User(user_id={user_id}) is not found")
        feedbacks = self._feedback_repository.fetch_list()

        if user.role == "support":
            return feedbacks

        # recentlyがTrue のときに、最後のコメント者がCSのものだけを返す
        if user.role == "customer":
            # result = []
            collection = FeedbackCollection(feedbacks)
            if recently:
                recently_filtered_collection = collection.filter_recently(...)

            return collection.filter_by_user_id(user_id=user_id)

            # for feedback in feedbacks:
            #     if feedback.user_id == user.user_id:
            #         if recently:
            #             if feedback.is_latest_comment_by_support():
            #                 result.append(feedback)
            #         else:
            #             result.append(feedback)
            # return result

        raise RuntimeError(f"Unknown user.role = {user.role}")


class FeedbackFetchHandler:
    @inject
    def __init__(
        self, user_repository: UserRepository, feedback_repository: FeedbackRepository
    ):
        self._user_repository = user_repository
        self._feedback_repository = feedback_repository

    def execute(self, user_id: int, feedback_id: str) -> Feedback:
        user = self._user_repository.fetch(user_id)
        if user is None:
            raise RuntimeError(f"User(user_id={user_id}) is not found")

        feedback = None
        for f in self._feedback_repository.fetch_list():
            if f.feedback_id == feedback_id:
                feedback = f
                break
        if feedback is None:
            raise RuntimeError(f"Feedback(feedback_id={feedback_id}) is not found")

        if user.role == "support":
            return feedback

        if user.role == "customer" and feedback.user_id == user.user_id:
            return feedback

        raise RuntimeError(f"Unknown user.role = {user.role}")


class FeedbackUpdateHandler:
    @inject
    def __init__(
        self, user_repository: UserRepository, feedback_repository: FeedbackRepository
    ):
        self._user_repository = user_repository
        self._feedback_repository = feedback_repository

    def execute(
        self,
        user_id: int,
        feedback_id: str,
        status: typing.Optional[str] = None,
        support_comment: typing.Optional[str] = None,
    ) -> Feedback:
        user = self._user_repository.fetch(user_id)
        if user is None:
            raise RuntimeError(f"User(user_id={user_id}) is not found")

        if user.role != "support":
            raise RuntimeError(
                f"PermissionError: User(user_id={user_id}, role={user.role}) is not editable for feedback."
            )

        feedback = None
        for f in self._feedback_repository.fetch_list():
            if f.feedback_id == feedback_id:
                feedback = f
                break
        if feedback is None:
            raise RuntimeError(f"Feedback(feedback_id={feedback_id}) is not found")

        if status:
            feedback = feedback.modify(status=status)
        if support_comment:
            feedback = feedback.modify(support_comment=support_comment)

        self._feedback_repository.save(feedback)
        return feedback


class FeedbackCommentCreateHandler:
    @inject
    def __init__(
        self, user_repository: UserRepository, feedback_repository: FeedbackRepository
    ):
        self._user_repository = user_repository
        self._feedback_repository = feedback_repository

    def execute(self, user_id: int, feedback_id: str, body: str) -> Feedback:
        user = self._user_repository.fetch(user_id)
        if user is None:
            raise RuntimeError(f"User(user_id={user_id}) is not found")

        feedback = None
        for f in self._feedback_repository.fetch_list():
            if f.feedback_id == feedback_id:
                feedback = f
                break
        if feedback is None:
            raise RuntimeError(f"Feedback(feedback_id={feedback_id}) is not found")

        if user.role == "customer" and feedback.user_id != user.user_id:
            raise RuntimeError(
                f"Feedback(feedback_id={feedback_id}) is not accessible from User(user_id={user_id})"
            )

        now = datetime.datetime.utcnow()
        comment = FeedbackComment(user_id=user.user_id, body=body, created_at=now)
        feedback.comments.append(comment)

        self._feedback_repository.save(feedback)
        return feedback
