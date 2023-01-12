from random import randint
from time import sleep
import os
from pathlib import Path
from _pytest.runner import runtestprotocol

import pytest
import inspect

import importlib


@pytest.fixture(scope="function", autouse=True)
def wait_fixture():
    sleep(randint(2, 3))
    yield
    sleep(randint(2, 3))


#Задание №1

#Недоделанное решение
#test_duration_over = pytest.StashKey[bool]()
#test_duration = pytest.StashKey[str]()
#
#def pytest_runtest_protocol(item: pytest.Item, nextitem):
#    reports = runtestprotocol(item, nextitem=nextitem)
#    for report in reports:
#        test_duration = 0
#        if report.when == 'call' or report.when == 'setup' or report.when == 'teardown':
#            test_duration += report.duration
#            if test_duration > 1:
#                item.stash[test_duration_over] = True
#                item.stash[test_duration] = f"Длительность теста {item.name} првышает 1 секунду ({test_duration} секунд)"
#
#def pytest_sessionfinish(session):
#    for item in session.items:
#        if item.stash[test_duration_over]:
#             print(item.stash[test_duration])


# Правильное решение
def pytest_report_teststatus(report, config):
    duration = config.stash.get(report.nodeid.replace(":", "_"), 0)
    # При каждом изменении  статуса теста в переменной
    # report.nodeid фисируется значение report.duration + то ,что уже было в report.nodeid
    # Это и будет время прохождения всех статусов тестом
    config.stash[report.nodeid.replace(":", "_")] = report.duration + duration


def pytest_sessionfinish(session):
    for item in session.items:
        duration = session.config.stash.get(item.nodeid.replace(":", "_"), 0)
        #Забираем то, что сложилось в nodeid через session.config в перемунную duration для читабельности
        # config общий для сессии и хука teststatus
        if duration > 7:
            print(item.nodeid, session.config.stash.get(item.nodeid.replace(":", "_"), 0))  # 2ой параметр -это duration


#  config объект конфигурации pytest.
#  stash хранилище информации о конфигурации
#  get получить значение по ключу
#  item.nodeid == report.nodeid  id теста
#  replace(":", "_")  замена в адресе элмента ":" на "_". item.nodeid это адрес? Тогда откуда берется длительность?


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
