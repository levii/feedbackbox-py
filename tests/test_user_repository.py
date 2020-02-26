from handlers import UserRepository
from infra import Repository
from infra import Store
from models import User
from tests.conftest_container import container


class TestUserRepository:
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

    def test_create_user(self):
        assert len(self.store.users) == 0

        user = User(name="Test User", role="support")
        self.user_repository.save(user)
        assert user.user_id == 1

        user = User(name="Test User", role="support")
        self.user_repository.save(user)
        assert user.user_id == 2

    def test_fetch_user(self):
        assert len(self.store.users) == 0

        user = User(name="Test User", role="support")
        self.user_repository.save(user)
        assert user.user_id == 1

        fetched_user = self.user_repository.fetch(user_id=1)
        assert fetched_user == user
