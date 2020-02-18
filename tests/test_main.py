import pickle
import typing
import os
import datetime
import uuid

import main

from infra import Store


class TestMain:
    def _execute(self, argv: typing.List[str]) -> typing.Tuple[typing.Optional[int], Store]:
        if not os.path.exists("tmp"):
            os.mkdir("tmp")
        t = int(datetime.datetime.utcnow().timestamp())
        database_file = os.path.join("tmp", f"{t}.{uuid.uuid4()}.pickle")

        ret = main.main(argv=argv, database_file=database_file)

        if os.path.exists(database_file):
            with open(database_file, "rb") as file:
                store = pickle.load(file)
        else:
            store = Store()
        return ret, store

    def test_empty_args(self):
        ret, _ = self._execute(argv=[])
        assert ret is None

    def test_create_feedback(self):
        _, store = self._execute(argv=["main.py", "create-feedback"])
        assert len(store.feedbacks) == 1
