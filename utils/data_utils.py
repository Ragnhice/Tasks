import datetime
import math

from enum import Enum


def generate_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


@aqas.sub_step("Обновить словарь с величинами Enum и floats")   #Название шага для отчета в Jenkins
def update_dict_to_compare(dict_to_update: dict) -> dict:
    """
    Обновить словарь с ожидаемыми величинами,преобразуются Enum и floats

    :param dict_to_update: Исходный словарь
    """
    updated_dict = {}
    for key, value in dict_to_update.items():
        if isinstance(value, float):
            updated_dict[key] = int(value)
        elif isinstance(value, Enum):
            updated_dict[key] = value.value
        elif isinstance(value, (list, set)):
            updated_dict[key] = [update_dict_to_compare(i) for i in value]
        elif isinstance(value, dict):
            updated_dict[key] = update_dict_to_compare(value)
        else:
            updated_dict[key] = value
    return updated_dict


@aqas.sub_step("Обновить словарь с аргументами типа float")
def floor_round_in_dict(dict_to_update: dict, accuracy: int = 0) -> dict:
    """
    Обновить словарь с аргументами типа float,
    значения возвращаются c указанной точностью- количеством знаков после запятой

    :param dict_to_update: Исходный словарь
    :param accuracy: Точность- количество знаков после запятой
    """
    updated_dict = {}
    for key, value in dict_to_update.items():
        if isinstance(value, float):
            updated_dict[key] = math.floor(value * int("1" + "0" * accuracy)) / int("1" + "0" * accuracy)
        elif isinstance(value, dict):
            updated_dict[key] = floor_round_in_dict(value, accuracy)
        else:
            updated_dict[key] = value
    return updated_dict

# pylint: disable=too-many-locals


@aqas.sub_step("Проверка значений двух словарей на расхождения значений или отсутствующие ключи в словаре/словарях")
def compare_dicts(dict_expected: dict, dict_actual: dict, comp_keys: list):    # noqa: C901
    """
    Сравнивает значения переданных ключей двух словарей, расхождения фиксируются в виде исключения типа AssertionError.
    В двух словарях определяются значения по искомым ключам из заданного списка для их сравнения,
    словарь в исходном словаре(вложенность) обрабатывается  рекурсивно. Формируются списки с несовпадающими значениями,
    ненайденными ключами в одном/двух словаре/словарях и сообщение с соответствующей информацией об ошибках.

    :param dict_expected: Словарь с данными ожидаемых величин
    :param dict_actual: Словарь с данными актуальных величин
    :param comp_keys: Список с искомых ключей
    """
    assert dict_actual is not None, (
        f"Не возвращается актуальный словарь с ключами: '{', '.join(comp_keys)}' -имеет значение None")

    mismatched_values = ""
    miss_keys_dict_expected = []
    miss_keys_dict_actual = []
    miss_keys_overall = []

    def getval(key, dict_with_key):
        """Возвращает первое найденное совпадение по имени, если в словарях ключи дублируются"""
        res = "Not found"
        if key in dict_with_key:
            return dict_with_key[key]
        for i in dict_with_key:
            if isinstance(dict_with_key[i], dict):
                res = getval(key, dict_with_key[i])
        return res

    for key in comp_keys:
        value_actual = getval(key, dict_actual)
        value_expected = getval(key, dict_expected)
        if value_expected == "Not found" and value_actual == "Not found":
            miss_keys_overall.append(key)
        elif value_expected == "Not found" and value_actual != "Not found":
            miss_keys_dict_expected.append(key)
        elif value_actual == "Not found" and value_expected != "Not found":
            miss_keys_dict_actual.append(key)
        else:
            if value_expected != value_actual:
                mismatched_values += (f"Несовпадение по ключу ['{key}']: "
                                      f"'{value_expected}' != '{value_actual}'.\n'")

    assert_message = ""
    if miss_keys_dict_expected:
        assert_message += f"В словаре ожидаемых величин не найдены ключи: {', '.join(miss_keys_dict_expected)}.\n'"
    if miss_keys_dict_actual:
        assert_message += f"Ключи: '{', '.join(miss_keys_dict_actual)}' - не найдены в актуальном словаре.\n'"
    if miss_keys_overall:
        assert_message += f"Ключей: '{', '.join(miss_keys_overall)}' - нет в ожидаемом и актуальном словарях .\n'"
    if mismatched_values:
        assert_message += mismatched_values
    assert assert_message == "", f"{assert_message}"
