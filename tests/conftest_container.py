from injector import Injector
from injector import singleton

from infra import Repository

container = Injector()
container.binder.bind(Repository, to=Repository(), scope=singleton)
