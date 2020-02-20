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

    def _execute(self, args: typing.List[str]) -> Response:
        parser = main.build_parser()
        options = parser.parse_args(args)
        return main.main(mode=options.mode, args=options, injector=self.container)

    def test_list_feedbacks(self):
        response = self._execute(args=["feedback", "list", "--user=1"])
        assert response.mode == "feedback-list"
        assert response.status == 200
        assert len(response.message) == 0

    def test_create_feedback(self):
        response = self._execute(args="feedback create --title=タイトル --description=本文 --user_id=1".split(" "))
        assert response.mode == "feedback-create"
        assert response.status == 200
        assert len(response.message) == 1
        feedback = response.message[0]
        assert isinstance(feedback, Feedback)

        list_response = self._execute(args="feedback list --user_id=1".split(" "))
        assert list_response.mode == "feedback-list"
        assert list_response.status == 200
        assert len(list_response.message) == 1
        assert list_response.message == [feedback]
