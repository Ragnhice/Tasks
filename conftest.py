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
    pakage_name = "core"
    project_path = Path.cwd().parent
    module_path = Path(os.path.join(project_path, pakage_name))

    def get_files_from_path(module_path):
        files = []
        for x in module_path.iterdir():
            if "__init__" not in str(x):
                files.append(x)
        return files

    files = get_files_from_path(module_path)
    for file in files:
        name_module = (str(file).split("\\")[-1]).split(".")[0]
        module = importlib.import_module(pakage_name + "." + name_module)
        module_classes = {}
        for key, value in inspect.getmembers(module, inspect.isclass):
            module_classes[key] = value
        test_data = []
        for class_item in module_classes.values():
            class_methods = inspect.getmembers(module.class_item, inspect.isfunction)
            for method_item in class_methods:
                if method_item[0].startswith("__"):
                    continue
                if not inspect.getdoc(method_item[1]):
                    data = {}
                    data["doc"] = "Нет документации"
                    data["method"] = method_item[0]
                    data["class"] = str(class_item).split(".")[-1]
                    test_data.append(data)
        metafunc.parametrize("data", test_data)
