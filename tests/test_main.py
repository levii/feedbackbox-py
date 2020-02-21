import typing
import main

from infra import Repository
from infra import Response
from models import Feedback
from models import User
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

    def _execute(self, args: typing.Union[str,typing.List[str]]) -> Response:
        if isinstance(args, str):
            args = args.split(" ")
        parser = main.build_parser()
        options = parser.parse_args(args)
        return main.main(mode=options.mode, args=options, injector=self.container)

    def test_list_feedbacks(self):
        response = self._execute("feedback list --user=1")
        assert response.mode == "feedback-list"
        assert response.status == 200
        assert len(response.message) == 0

    def test_create_feedback(self):
        response = self._execute("feedback create --title=タイトル --description=本文 --user_id=1")
        assert response.mode == "feedback-create"
        assert response.status == 200
        assert len(response.message) == 1
        feedback = response.message[0]
        assert isinstance(feedback, Feedback)

        list_response = self._execute("feedback list --user_id=1")
        assert list_response.mode == "feedback-list"
        assert list_response.status == 200
        assert len(list_response.message) == 1
        assert list_response.message == [feedback]

    def test_scenario_1(self):
        create_user_response = self._execute(["user", "create", "--name='Test User'", "--role='customer'"])
        assert len(self.repository.store.users) == 1
        user: User = create_user_response.message[0]

        feedback_response = self._execute(
            f"feedback create --title='要望タイトル' --description='要望の本文' --user_id={user.user_id}"
        )
        feedback: Feedback = feedback_response.message[0]
        assert isinstance(feedback, Feedback)

        feedback_list_response = self._execute(f"feedback list --user_id={user.user_id}")
        feedbacks = feedback_list_response.message
        assert len(feedbacks) == 1
