from pathlib import Path
from _pytest.runner import runtestprotocol
from _pytest.python import Metafunc

import pytest
import inspect

import importlib

message = pytest.StashKey[str]()

def pytest_runtest_protocol(item: pytest.Item, nextitem, session: pytest.Session):
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        test_duration = 0
        if report.when == 'call' or report.when == 'setup' or report.when == 'teardown':
            test_duration += report.duration

        if test_duration > 7:
            session[message] += f"Тест {item.stash[item.name]} : {test_duration} секунд"

def pytest_sessionfinish(session: pytest.Session):
   if session[message]:
       print("Длительность следующих тестов первышает 7 секунд: " + session[message])


def pytest_generate_tests(metafunc: Metafunc) -> dict:
    """
    Вызывается при сборке тестовой функции c маркером test_case
    Проверяет наличие документации у методов класса модуля проекта

    :param data: metafunc Тестовая функция.

    """

    if 'test_case' not in metafunc.fixturenames:
        return
    path = Path("/Tasks/core")

    def get_files_from_path(path):
        files = []
        for x in path.iterdir():
            if x.is_dir():
                files.append(get_files_from_path(path))
            else:
                if "__init__" not in str(x):
                    files.append(x)
        return files

    files = get_files_from_path(path)

    for file in files:
        def load_from_module(module):
            return importlib.import_module(module)  # получение тестовых данных

        module = load_from_module(file)
        module_classes = {}
        for key, data in inspect.getmembers(module, inspect.isclass):
            module_classes[key] = data

        for class_item in module_classes.keys():
            class_methods = inspect.getmembers(module.class_item, inspect.ismethod)
            for function_item in class_methods:
                if not inspect.getdoc(module.class_item.function_item[0]):
                    data["doc"] = "Нет документации"
                    data['method'] = function_item[0]
                    data['class'] = class_item
                    metafunc.parametrize("data", data)
