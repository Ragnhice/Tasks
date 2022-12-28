import datetime
import pytest
#Допускается использование модулей _os_, _pathlib_, _importlib_



@pytest.fixture(autouse=True)
def check_duration():
    """
        Выводит название и время выполнения теста, полное (вместе с
        фикстурами) время выполнения которых заняло больше 7 секунд

    """

    start_time = datetime.datetime.now()
    yield
    stop_time = datetime.datetime.now()
    this_duration = (stop_time - start_time).total_seconds()
    assert this_duration < 7, f"Длительность теста {function.__name__}первышает 7 секунд"


@pytest.fixture(autouse=True)
def check_documentation(request, cache):
    """
    Проверяет наличие документации у методов классов модуля

    :param data:

    """
    #Для этого необходимо сгенерировать тестовые данные
    # при помощи  модуля inspect
    #Генерация тестов для проверки всех возможных классов без знания имени класса
