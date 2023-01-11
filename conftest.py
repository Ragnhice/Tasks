import os
from pathlib import Path
from _pytest.runner import runtestprotocol

import pytest
import inspect

import importlib

 Задание №1
 тесты запускаются по 2 раза и их проходит 10,а не 5
 Результат по завершению всех тестов  не вывелся
def pytest_runtest_protocol(item):
    reports = runtestprotocol(item)
    for report in reports:
        test_duration = 0
        if report.when == 'call' or report.when == 'setup' or report.when == 'teardown':
            test_duration += report.duration
        if test_duration > 1:
            print(f"Длительность теста {item.name} первышает 1 секунду ({test_duration} секунд)")

# Задание №2
def pytest_generate_tests(metafunc) -> list:
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

    test_data = []
    files = get_files_from_path(module_path)
    for file in files:
        name_module = (str(file).split("\\")[-1]).split(".")[0]
        module = importlib.import_module(pakage_name + "." + name_module)
        module_classes = {}
        for key, value in inspect.getmembers(module, inspect.isclass):
            module_classes[key] = value
        for class_item in module_classes.values():
            class_methods = inspect.getmembers(class_item, inspect.ismethod(class_item))
            for method_item in class_methods:
                if method_item[0].startswith("__"):
                    continue
                data = {}
                data["method"] = method_item[0]
                data["class"] = str(class_item).split(".")[-1][:-2]
                data["doc"] = inspect.getdoc(method_item[1])
                test_data.append(data)
    metafunc.parametrize("data", test_data)
