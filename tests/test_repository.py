import os
import typing
import uuid
import datetime

import main


class TestRepository:
    repository_file: typing.Optional[str] = None

    @classmethod
    def setup_class(cls):
        cls.test_dir = os.path.join(os.path.curdir, "tmp")
        if not os.path.exists(cls.test_dir):
            os.mkdir(cls.test_dir)

    def setup_method(self, _):
        t = int(datetime.datetime.utcnow().timestamp())
        self.repository_file = os.path.join(self.test_dir, f"test.{t}.{uuid.uuid4()}.pickle")

    def teardown_method(self):
        if self.repository_file and os.path.exists(self.repository_file):
            os.remove(self.repository_file)

    def test_init_repository(self):
        repo = main.Repository()
        assert isinstance(repo, main.Repository)

    def test_load_and_persistent(self):
        assert os.path.exists(self.repository_file) is False
        repo = main.Repository.load(filename=self.repository_file)
        repo.persistent()
        assert os.path.exists(self.repository_file) is True

        repo2 = main.Repository.load(filename=self.repository_file)
        assert repo.store.created_at == repo2.store.created_at

        repo3 = main.Repository()
        assert repo.store.created_at != repo3.store.created_at
