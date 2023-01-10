import os
from pathlib import Path
from _pytest.runner import runtestprotocol

import pytest
import inspect

import importlib

message = pytest.StashKey[str]()

def pytest_runtest_protocol(item: pytest.Item, nextitem):
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        test_duration = 0
        if report.when == 'call' or report.when == 'setup' or report.when == 'teardown':
            test_duration += report.duration
        if test_duration > 7:
            print(f"Длительность теста {item.name} первышает 7 секунд ({test_duration} секунд)")


def pytest_generate_tests(metafunc) -> dict:
    """
    Вызывается при сборке тестовой функции c маркером test_case
    Проверяет наличие документации у методов класса модуля проекта

    :param data: metafunc Тестовая функция.

    """

    if 'data' not in metafunc.fixturenames:
        return

    project_path = Path.cwd().parent
    module_path = Path(os.path.join(project_path, 'core'))

    def get_files_from_path(module_path):
        files = []
        for x in module_path.iterdir():
            if "__init__" not in str(x):
                files.append(x)
        return files

    files = get_files_from_path(module_path)
    for file in files:
        module = importlib.import_module("core", path = file)
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
