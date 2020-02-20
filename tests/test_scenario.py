from handlers import FeedbackCreateHandler
from handlers import UserRepository
from infra import Repository
from infra import Store
from models import Feedback
from models import User
from tests.conftest_container import container


class TestScenario:
    @classmethod
    def setup_class(cls):
        cls.container = container
        cls.repository: Repository = cls.container.get(Repository)
        cls.user_repository: UserRepository = cls.container.get(UserRepository)

    def teardown_method(self, _):
        self.repository.reset()

    @property
    def store(self) -> Store:
        return self.repository.store

    def test_usecase_create_feedback_by_customer(self):
        customer_user = User(name="Customer User", role="customer")
        self.user_repository.save(customer_user)

        create_handler: FeedbackCreateHandler = self.container.get(FeedbackCreateHandler)
        title = "要望のタイトル"
        description = "要望の本文"
        feedback = create_handler.execute(title, description, user_id=customer_user.user_id)
        assert isinstance(feedback, Feedback)
