import datetime
import pytest
import inspect


@pytest.fixture(scope="session", autouse=True)
def check_duration(request):
    """
        Выводит название и время выполнения теста, полное (вместе с
        фикстурами) время выполнения которых заняло больше 7 секунд

    :param data: request

    """

    start_time = datetime.datetime.now()
    yield
    stop_time = datetime.datetime.now()
    this_duration = (stop_time - start_time).total_seconds()
    assert this_duration > 7, f"Длительность теста {request.node.name} первышает 7 секунд"


@pytest.fixture(scope="session", autouse=True)    # как применить фикстуру не к тесту, а ко всем модулям в проекте?
def check_documentation(module_name):             # как передавать имя модулей?
    """
    Проверяет наличие документации у методов классов по имени модуля

    :param data: module_name Имя модуля, методы в классах которого нужно проверить

    """
    module_classes = {}
    for key, data in inspect.getmembers(module_name, inspect.isclass):
        module_classes[key] = data

    for class_item in module_classes.keys():
        class_functions = inspect.getmembers(module_name.class_item, inspect.isfunction)
        for function_item in class_functions:
            assert inspect.getdoc(module_name.class_item.function_item[0]), (
                f"Нет  документации у метода {function_item[0]} в классе {class_item}")
