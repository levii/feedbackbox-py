import typing
import main

from infra import Repository
from infra import Response
from models import Feedback
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

    def _execute(self, argv: typing.List[str]) -> Response:
        return main.main(argv=argv, injector=self.container)

    def test_empty_args(self):
        response = self._execute(argv=[])
        assert isinstance(response, Response)
        assert response.status == 500

    def test_list_feedbacks(self):
        response = self._execute(argv=["main.py", "list-feedbacks"])
        assert response.mode == "list-feedbacks"
        assert response.status == 200
        assert len(response.message) == 0

    def test_create_feedback(self):
        response = self._execute(argv=["main.py", "create-feedback"])
        assert response.mode == "create-feedback"
        assert response.status == 200
        assert len(response.message) == 1
        feedback = response.message[0]
        assert isinstance(feedback, Feedback)

        list_response = self._execute(argv=["main.py", "list-feedbacks"])
        assert list_response.mode == "list-feedbacks"
        assert list_response.status == 200
        assert len(list_response.message) == 1
        assert list_response.message == [feedback]
