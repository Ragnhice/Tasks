import random
from abc import ABC, abstractmethod

from adapters.api.api_adapter import ApiAdapter

class Basic(ABC):
    """ Базовый абстрактный класс"""

    @property
    @abstractmethod
    def id(self):
        pass

    @property
    @abstractmethod
    def uuid(self):
        pass

class Create(ABC):
    """Абстрактный класс с методом создания"""

    @abstractmethod
    def create(self):
        pass

class Delete(ABC):
    """Абстрактный класс с методом удаления"""

    @abstractmethod
    def delete(self):
        pass

class User(Basic,Create, Delete):
    def __init__(self, name, id, uuid):
        self.name = name
        self.__id = id
        self.__uuid = uuid

    @property
    def id(self) -> int:
        return self.__id

    @property
    def uuid(self) -> str:
        return self.__uuid

    @property
    def salary(self) -> int:
        return 1000000

    def create(self):
        ApiAdapter().call_create(self.name, self.uuid)

    def delete(self):
        ApiAdapter().call_delete(self.name, self.uuid)


class Car(Basic,Create, Delete):
    def __init__(self, name, id, uuid):
        self.name = name
        self.__id = id
        self.__uuid = uuid

    @property
    def id(self) -> int:
        return self.__id

    @property
    def uuid(self) -> str:
        return self.__uuid

    def create(self):
        ApiAdapter().call_create(self.name, self.uuid)

    def delete(self):
        ApiAdapter().call_delete(self.name, self.uuid)

    @staticmethod
    def drive():
        print("Машина занята")


class Track(Basic,Create, Delete):
    def __init__(self, name, id, uuid):
        self.name = name
        self.__id = id
        self.__uuid = uuid

    @property
    def id(self) -> int:
        return self.__id

    @property
    def uuid(self) -> str:
        return self.__uuid

    def create(self):
        ApiAdapter().call_create(self.name, self.uuid)

    def delete(self):
        ApiAdapter().call_delete(self.name, self.uuid)

    @staticmethod
    def is_free() -> bool:
        return bool(random.getrandbits(1))


class City(Basic,Create):
    def __init__(self, name, id, uuid):
        self.name = name
        self.__id = id
        self.__uuid = uuid

    @property
    def id(self) -> int:
        return self.__id

    @property
    def uuid(self) -> str:
        return self.__uuid

    def create(self):
        ApiAdapter().call_create(self.name, self.uuid)


class Country(Basic):
    def __init__(self, name, id, uuid):
        self.name = name
        self.__id = id
        self.__uuid = uuid

    @property
    def id(self) -> int:
        return self.__id

    @property
    def uuid(self) -> str:
        return self.__uuid
