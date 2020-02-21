import copy
import datetime
import typing
import uuid

from injector import inject

from infra import Repository
from infra import Store
from models import Feedback
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

    def execute(self, name: str, role: str) -> User:
        user = User(name, role)
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


class FeedbackFetchListHandler:
    @inject
    def __init__(self, feedback_repository: FeedbackRepository):
        self._feedback_repository = feedback_repository

    def execute(self, user: User) -> typing.List[Feedback]:
        feedbacks = self._feedback_repository.fetch_list()

        if user.role == "support":
            return feedbacks

        if user.role == "customer":
            result = []
            for feedback in feedbacks:
                if feedback.user_id == user.user_id:
                    result.append(feedback)
            return result

        raise RuntimeError(f"Unknown user.role = {user.role}")
