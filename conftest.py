from random import randint
from time import sleep
import os
from pathlib import Path

import pytest
import inspect

import importlib
import importlib.machinery



@pytest.fixture(scope="function", autouse=True)
def wait_fixture():
    sleep(randint(2, 3))
    yield
    sleep(randint(2, 3))



def pytest_report_teststatus(report, config):
    #этот хук выполняется 3 раза для каждого теста
    duration = config.stash.get(report.nodeid.replace(":", "_"), 0)
    #забираем значение по ключу (полное название теста, заменяя : на _, так как с : не записывается в stash),
    # если такого ключа в stash нет, то оно равно 0

    config.stash[report.nodeid.replace(":", "_")] = report.duration + duration
    # При каждом изменении  статуса теста в переменной
    # report.nodeid фисируется значение report.duration + то ,что уже было в report.nodeid
    # Это и будет время прохождения всех статусов тестом

def pytest_sessionfinish(session):
    for item in session.items:
        duration = session.config.stash.get(item.nodeid.replace(":", "_"), 0)
        #Забираем то, что сложилось в nodeid через session.config в перемунную duration для читабельности
        # config общий для сессии и хука teststatus
        if duration > 7:
            print(item.nodeid, session.config.stash.get(item.nodeid.replace(":", "_"), 0))  # 2ой параметр -это duration


def pytest_addoption(parser):
    """Declaring the command-line options for test run"""
    parser.addoption("--api_healthcheck",
                     action="store_true",
                     default=False,
                     help="start with checking api for ready to test")


def pytest_sessionstart(session):
    """Завершение тестовой сессии при наличии ConnectionError в ответе запроса"""
    print("Тестовая сессия запущена")
    if not session.config.getoption("--api_healthcheck"):
        return

    for i in range(4):
        try:
            ApiGatewayAdapter().query("startupVersion")   #адаптер ApiGatewayAdapter в библиотеке фреймворка
        except exceptions.ConnectionError:                #exceptions также в библиотеке фреймворка
            if i < 3:
                sleep(20)
        else:
            print("Проверка API прошла успешно")
            return
    pytest.exit("API не готово к тестированию", returncode=1)

def pytest_generate_tests(metafunc) -> list:
    """
    Вызывается при сборке тестовой функции c маркером test_case
    Проверяет наличие документации у методов класса модуля проекта

    :param data: metafunc Тестовая функция.

    """

    if 'data' not in metafunc.fixturenames:
        return
    pakage_name = "core"                 #можно вынести в константы
    project_path = Path.cwd().parent
    module_path = Path(os.path.join(project_path, pakage_name))

    def get_files_from_path(module_path):           #можно вынести в утилиты
        files = []
        for x in module_path.iterdir():
            if "__init__" not in str(x):
                files.append(x)
        return files

    test_data = []
    files = get_files_from_path(module_path)
    for file in files:
        loader = importlib.machinery.SourceFileLoader('module', str(file))
        spec = importlib.util.spec_from_loader('module', loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        #или
        #name_module = (str(file).split("\\")[-1]).split(".")[0]
        #module = importlib.import_module(pakage_name + "." + name_module)
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

#короткая версия
def pytest_generate_tests(metafunc):
    """
    Вызывается при сборке тестовой функции c маркером test_case
    Проверяет наличие документации у методов класса модуля проекта

    :param data: metafunc Тестовая функция.

    """

    if "data" in metafunc.fixturenames:
        test_data = []
        files = [f"core.{x.rstrip('.py')}" for x in os.listdir("core") if x[0:2] != "__"]
        for file_ in files:
            inspect.getmembers(__import__(file_))
        for name, module in [x for x in inspect.getmembers(__import__("core")) if x[0][0:2] != "__"]:
            for class_name in [x for x in inspect.getmembers(module) if x[0][0:2] != "__"]:
                for method in [x for x in inspect.getmembers(class_name[1]) if x[0][0:2] != "__"]:
                    test_data.append({"class": class_name[0], "method": method[0], "doc": inspect.getdoc(method[1])})
        metafunc.parametrize("data", test_data)