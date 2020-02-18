import typing
import main

from infra import Repository
from infra import Store
from tests.conftest_container import container


class TestMain:
    @classmethod
    def setup_class(cls):
        cls.container = container

    @property
    def repository(self) -> Repository:
        return self.container.get(Repository)

    def teardown_method(self, _):
        self.repository.reset()

    def _execute(self, argv: typing.List[str]) -> typing.Tuple[typing.Optional[int], Store]:
        ret = main.main(argv=argv, injector=self.container)
        return ret, self.repository.store

    def test_empty_args(self):
        ret, _ = self._execute(argv=[])
        assert ret is None

    def test_create_feedback(self):
        _, store = self._execute(argv=["main.py", "create-feedback"])
        assert len(store.feedbacks) == 1
