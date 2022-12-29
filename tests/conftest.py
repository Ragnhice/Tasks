import datetime
import pytest
import inspect


def pytest_generate_tests(metafunc):
    """
    Проверяет наличие документации у методов классов по имени модуля

    :param data: metafunc Тестовая функция.

    """
    module_classes = {}
    for key, data in inspect.getmembers(metafunc.module, inspect.isclass):
        module_classes[key] = data

    for class_item in module_classes.keys():
        class_functions = inspect.getmembers(metafunc.module.class_item, inspect.isfunction)
        for function_item in class_functions:
            assert inspect.getdoc(metafunc.module.class_item.function_item[0]), (
                f"Нет  документации у метода {function_item[0]} в классе {class_item}")




 #Вар1 item.stash

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





#Вар2 Обертка
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    global start_time
    start_time = datetime.datetime.now()

    outcome = yield

    location,stop_time = outcome.get_result()
    test_duration = (stop_time - start_time).total_seconds()
    if test_duration > 7:
         print(f"Длительность теста {location[2]} {test_duration} секунд первышает 7 секунд")


@pytest.hookimpl(trylast=True)
def pytest_runtest_logfinish(nodeid, location):
    stop_time = datetime.datetime.now()
    return (location,stop_time)




 #Вар3
@pytest.hookimpl(tryfirst=True)
@pytest.hookspec(firstresult=True)
def pytest_runtest_call(item):                # хук pytest_runtest_call - Вызывается для запуска теста
    global start_time
    start_time = datetime.datetime.now()
                                     #location = (filename, lineno, testname)

@pytest.hookimpl(trylast=True)
def pytest_runtest_logfinish(nodeid, location, request):            # хук Вызывается в конце выполнения протокола runtest
    stop_time = datetime.datetime.now()
    test_duration = (stop_time - start_time).total_seconds()
    if test_duration > 7:
        print(f"Длительность теста {request.node.name} {test_duration} секунд первышает 7 секунд")
        #print(f"Длительность теста {location[2]} {test_duration} секунд первышает 7 секунд")




# Вар4 неправильный
@pytest.fixture(scope="function", autouse=True)
def check_duration(request):
    """
        Выводит название и время выполнения теста, полное (вместе с
        фикстурами) время выполнения которых заняло больше 7 секунд

    :param data: request

    """

   # разобраться с хуками в пайтесте
   #Тест в пайтесте делится на 3 части: 1 - запуск всех фикстур, 2 - запуск теста, 3 - завершение всех фикстур
   #  поэтому делать фикстуру для измерения времени длительности всего запуска теста (вместе с фикстурами) некорректно.
    start_time = datetime.datetime.now()
    yield
    stop_time = datetime.datetime.now()
    test_duration = (stop_time - start_time).total_seconds()
    assert test_duration > 7, f"Длительность теста {request.node.name} {test_duration} секунд первышает 7 секунд,"



#генератор тестов, а не фикстура
#@pytest.fixture(scope="session", autouse=True)    # как применить фикстуру не к тесту, а ко всем модулям в проекте?
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
