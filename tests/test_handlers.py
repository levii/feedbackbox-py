from handlers import FeedbackCreateHandler
from handlers import FeedbackRepository
from infra import Repository
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
        self.handler.execute(title=title, description=description)

        feedbacks = self.feedback_repository.fetch_list()
        assert len(feedbacks) == 1
        assert feedbacks[0].title == title
        assert feedbacks[0].description == description
