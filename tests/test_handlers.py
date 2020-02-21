import pytest

from handlers import FeedbackCommentCreateHandler
from handlers import FeedbackCreateHandler
from handlers import FeedbackFetchListHandler
from handlers import FeedbackRepository
from handlers import UserRepository
from infra import Repository
from models import Feedback
from models import User
from tests.conftest_container import container


class TestFeedbackCreateHandler:
    @classmethod
    def setup_class(cls):
        cls.container = container
        cls.handler: FeedbackCreateHandler = cls.container.get(FeedbackCreateHandler)
        cls.feedback_repository: FeedbackRepository = cls.container.get(FeedbackRepository)

    @property
    def repository(self) -> Repository:
        return self.container.get(Repository)

    def teardown_method(self, _):
        self.repository.reset()

    def test_create_feedback_success(self):
        assert self.feedback_repository.fetch_list() == []
        title = "改善要望のタイトル"
        description = "こういう改善をしてほしい"
        self.handler.execute(title=title, description=description, user_id=123)

        feedbacks = self.feedback_repository.fetch_list()
        assert len(feedbacks) == 1
        assert feedbacks[0].title == title
        assert feedbacks[0].description == description


class TestFeedbackFetchListHandler:
    customer_user = None
    customer_other_user = None
    support_user = None

    customer_user_feedback = None
    customer_other_user_feedback = None

    @classmethod
    def setup_class(cls):
        cls.container = container
        cls.repository: Repository = cls.container.get(Repository)
        cls.create_handler: FeedbackCreateHandler = cls.container.get(FeedbackCreateHandler)
        cls.fetch_handler: FeedbackFetchListHandler = cls.container.get(FeedbackFetchListHandler)
        cls.user_repository: UserRepository = cls.container.get(UserRepository)
        cls.feedback_repository: FeedbackRepository = cls.container.get(FeedbackRepository)

    def setup_method(self, _):
        self.customer_user = User(name="Test Customer User", role="customer")
        self.user_repository.save(self.customer_user)
        self.customer_user_feedback = self.create_handler.execute(
            title="要望タイトル",
            description="要望の本文",
            user_id=self.customer_user.user_id,
        )

        self.customer_other_user = User(name="Test Customer Other User", role="customer")
        self.user_repository.save(self.customer_other_user)
        self.customer_other_user_feedback = self.create_handler.execute(
            title="要望タイトル",
            description="要望の本文",
            user_id=self.customer_other_user.user_id,
        )

        self.support_user = User(name="Support User", role="support")
        self.user_repository.save(self.support_user)

    def teardown_method(self, _):
        self.repository.reset()

    def test_fetch_by_customer(self):
        feedbacks = self.fetch_handler.execute(user_id=self.customer_user.user_id)
        assert len(feedbacks) == 1
        assert feedbacks[0] == self.customer_user_feedback

    def test_fetch_by_support(self):
        feedbacks = self.fetch_handler.execute(user_id=self.support_user.user_id)
        assert len(feedbacks) == 2


class TestFeedbackCommentCreateHandler:
    customer_user = None
    customer_other_user = None
    support_user = None

    customer_user_feedback = None

    @classmethod
    def setup_class(cls):
        cls.container = container
        cls.repository: Repository = cls.container.get(Repository)
        cls.create_handler: FeedbackCreateHandler = cls.container.get(FeedbackCreateHandler)
        cls.user_repository: UserRepository = cls.container.get(UserRepository)
        cls.feedback_repository: FeedbackRepository = cls.container.get(FeedbackRepository)

        cls.handler: FeedbackCommentCreateHandler = cls.container.get(FeedbackCommentCreateHandler)

    def setup_method(self, _):
        self.customer_user = User(name="Test Customer User", role="customer")
        self.user_repository.save(self.customer_user)
        self.customer_user_feedback = self.create_handler.execute(
            title="要望タイトル",
            description="要望の本文",
            user_id=self.customer_user.user_id,
        )

        self.customer_other_user = User(name="Test Customer Other User", role="customer")
        self.user_repository.save(self.customer_other_user)

        self.support_user = User(name="Support User", role="support")
        self.user_repository.save(self.support_user)

    def teardown_method(self, _):
        self.repository.reset()

    def test_comment_by_missing_user(self):
        with pytest.raises(RuntimeError):
            self.handler.execute(
                user_id=99999,
                feedback_id=self.customer_user_feedback.feedback_id,
                body="comment body",
            )

    def test_comment_by_missing_feedback(self):
        with pytest.raises(RuntimeError):
            self.handler.execute(
                user_id=self.customer_user.user_id,
                feedback_id="missing-feedback-id",
                body="comment body",
            )

    def test_comment_by_feedback_customer(self):
        assert self.customer_user_feedback.comments == []
        self.handler.execute(
            user_id=self.customer_user.user_id,
            feedback_id=self.customer_user_feedback.feedback_id,
            body="コメントだよ"
        )

        feedbacks = self.feedback_repository.fetch_list()
        feedback = None
        for f in feedbacks:
            if f.feedback_id == self.customer_user_feedback.feedback_id:
                feedback = f
                break
        assert isinstance(feedback, Feedback)
        assert len(feedback.comments) == 1

        assert feedback.comments[0].body == "コメントだよ"

    def test_comment_by_support_user(self):
        assert self.customer_user_feedback.comments == []
        self.handler.execute(
            user_id=self.support_user.user_id,
            feedback_id=self.customer_user_feedback.feedback_id,
            body="コメントだよ"
        )

        feedbacks = self.feedback_repository.fetch_list()
        feedback = None
        for f in feedbacks:
            if f.feedback_id == self.customer_user_feedback.feedback_id:
                feedback = f
                break
        assert isinstance(feedback, Feedback)
        assert len(feedback.comments) == 1

        assert feedback.comments[0].body == "コメントだよ"

    def test_comment_failed_by_other_customer(self):
        assert self.customer_user_feedback.comments == []

        with pytest.raises(RuntimeError):
            self.handler.execute(
                user_id=self.customer_other_user.user_id,
                feedback_id=self.customer_user_feedback.feedback_id,
                body="コメントだよ"
            )
