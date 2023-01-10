from time import sleep

import pytest


@pytest.mark.test_case("test_case_")
@pytest.mark.parametrize("time", list(range(7, 10)))
def test_time(time):
    sleep(time)


@pytest.mark.test_case("test_case")
def test_documentation(data):
    assert data["doc"], f"Метод {data['method']} класса {data['class']} не имеет документации"
