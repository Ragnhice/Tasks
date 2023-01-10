
from _pytest.runner import runtestprotocol

import pytest


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
