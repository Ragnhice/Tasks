from random import randint
from time import sleep
import importlib

import datetime
import pytest
import inspect


@pytest.fixture(scope="function", autouse=True)
def wait_fixture():
    sleep(randint(2, 3))
    yield
    sleep(randint(2, 3))


def pytest_generate_tests(metafunc: "Metafunc") -> dict:
    """
    Вызывается при сборке тестовой функции c маркером test_case
    Проверяет наличие документации у методов класса модуля проекта
    :param data: metafunc Тестовая функция.
    """

    if 'data' not in metafunc.fixturenames:
        return

    module = importlib.import_module('core.user')

    module_classes = {}
    for key, value in inspect.getmembers(module, inspect.isclass):
        module_classes[key] = value
    test_data = []
    for class_item in module_classes.values():
        class_functions = inspect.getmembers(class_item, inspect.ismethod)    #getmembers принимает путь типом объект
        for function_item in class_functions:
            if function_item[0].startswith('__'):
                continue
            if not inspect.getdoc(function_item[1]):
                data = {}
                data["doc"] = "Нет документации"
                data['method'] = function_item[0]
                data['class'] = str(class_item).split(".")[-1]
                test_data.append(data)
    metafunc.parametrize("data", test_data)

 #Задание 2. Решение с item.stash
been_start_time = pytest.StashKey[bool]()
start_time = pytest.StashKey[str]()
name_test_started = pytest.StashKey[str]()
message = pytest.StashKey[str]()  #Общее сообщение для сессии после того как все тесты пройдут

def pytest_sessionfinish(session: pytest.Session, exitstatus):
   if session[message]:
       print("Длительность следующих тестов первышает 7 секунд: " + session[message])

def pytest_runtest_setup(item: pytest.Item) -> None:                # includes obtaining the values of fixtures required by the item
    item.stash[been_start_time] = True
    item.stash[start_time] = datetime.datetime.now()

def pytest_runtest_logstart(nodeid, location, item: pytest.Item):     #location = (filename, lineno, testname)
    if item.stash[been_start_time]:                                   # возможно ли location передать в другой хук?
        item.stash[name_test_started] = location[2]

def pytest_runtest_teardown(item: pytest.Item,session: pytest.Session) -> None:            # includes running the teardown phase of fixtures required by the item
    stop_time = datetime.datetime.now()
    if item.stash[been_start_time]:
        test_duration = (stop_time - item.stash[start_time]).total_seconds()
        if test_duration > 7:
            session[message] += f"Тест {item.stash[name_test_started]} : {test_duration} секунд "
