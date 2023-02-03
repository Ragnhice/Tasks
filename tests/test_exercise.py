# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
from random import choice

import allure
import aqas
import pytest
from faker import Faker

from models.api.api_gateway_adapter import ApiGatewayAdapter
from utils.constants import API
from utils.data_utils import compare_dicts, update_dict_to_compare
from utils.enums import (
    ExTypeEnum,
    NullConstantsEnum,
    PrecipitationEnum,
    SeasonEnum,
    ShooterPositionEnum,
    TagScopesEnum,
    TargetTypeEnum,
)


@allure.parent_suite("api")
@allure.suite("ExerciseApi")
@allure.sub_suite("crud")
class TestsCrudExercise:
    EXERCISE_ID = ""
    COMMAND_MOVE_ID = ""
    OBJECT_ID_CAMERA = ""
    OBJECT_ID_IPSC = ""
    TAG_ID = ""

    @pytest.mark.dependency()
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-491")
    @allure.title("objects params for add ex")
    def test_get_objects_params(self):
        with aqas.step("Отправка запроса"):
            objects_params = ApiGatewayAdapter().query("objects")

        with aqas.step("Проверка наличия ответа"):
            assert objects_params, "Нет ответа от запроса"

        TestsCrudExercise.COMMAND_MOVE_ID = objects_params[0]["availableCommands"][0]["id"]

    @pytest.mark.dependency(depends=["test_get_objects_params"], scope="class")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-402")
    @allure.title("create_exercise")
    def test_create_exercise(self):    # noqa: CFQ001
        create_exercise_input = {
            "addExercise": {
                "exerciseCreateInput": {
                    "name": Faker().first_name(),
                    "description": Faker().first_name(),
                    "environment": {
                        "endOnWrongLane": Faker().boolean(),
                        "timeLimit": choice(API.TIMELIMIT),
                        "season": SeasonEnum.SUMMER,
                        "shooterPosition": ShooterPositionEnum.KNEES,
                        "hour": Faker().pyfloat(min_value=0, max_value=23),
                        "precipitation": PrecipitationEnum.MIDDLE,
                        "visibility": Faker().pyfloat(min_value=1, max_value=4000),
                        "temperature": Faker().pyfloat(min_value=-50, max_value=50),
                        "pressure": Faker().pyfloat(min_value=700, max_value=800),
                        "windDirection": Faker().pyfloat(min_value=0, max_value=360),
                        "windSpeed": Faker().pyfloat(min_value=0, max_value=30),
                        "humidity": Faker().pyfloat(min_value=1, max_value=50),
                        "altitude": Faker().pyfloat(min_value=1, max_value=50),
                        "hitLimit": Faker().random_int(1, 10),
                        "targetLimit": Faker().random_int(1, 10),
                        "scoreLimit": Faker().random_int(1, 10),
                        "tracerEveryNShot": Faker().random_int(1, 10),
                    },
                    "exerciseObjects": [{
                        "targetType": TargetTypeEnum.NOTTARGET,
                        "objectId": API.OBJECT_GUUD_CAMERA,
                        "name": API.OBJECT_NAME_CAMERA,
                        "isCommandsCycled": Faker().boolean(),
                        "index": API.OBJECT_INDEX_CAMERA,
                        "position": API.POSITION_CAMERA,
                        "rotation": API.ROTATION_CAMERA,
                        "scale": API.SCALE_CAMERA,
                        "shotReactDistance": Faker().pyfloat(min_value=1, max_value=800),
                        "exerciseCommands": {
                            "name": API.COMMANDS_NAME_CAMERA,
                            "params": API.COMMANDS_PARAMS_CAMERA,
                            "index": API.OBJECT_INDEX_CAMERA,
                            "commandId": TestsCrudExercise.COMMAND_MOVE_ID,
                            "eventExpression": {
                                "index": API.EVENT_EXPRESSION_INDEX_CAMERA,
                                "event": {
                                    "index": API.CAMERA_EVENT_INDEX,
                                    "params": Faker().first_name(),
                                },
                                "leftOperand": NullConstantsEnum.NULL_VALUE,
                                "operator": NullConstantsEnum.NULL_VALUE,
                                "rightOperand": NullConstantsEnum.NULL_VALUE,
                            },
                        },
                    }, {
                        "objectId": API.OBJECT_GUUD_IPSC_5,
                        "name": API.OBJECT_NAME_IPSC_5,
                        "isCommandsCycled": Faker().boolean(),
                        "index": API.OBJECT_INDEX_IPSC_5,
                        "position": API.POSITION_IPSC_5,
                        "rotation": API.ROTATION_IPSC_5,
                        "scale": API.SCALE_IPSC_5,
                        "shotReactDistance": Faker().pyfloat(min_value=1, max_value=800),
                        "targetType": TargetTypeEnum.ENEMY,
                        "exerciseCommands": [],
                    }],
                    "exerciseWeaponPresets": [{
                        "weaponTypeId": API.WEAPON_ID_EX,
                        "ammoTypeId": API.AMMO_ID_EX,
                        "exerciseId": API.EX_ID_SHOOTING_RANGE,
                    }],
                    "sceneId": API.SCENE_ID_SHOOTING_RANGE,
                    "type": ExTypeEnum.EX3D,
                    "deleted": False,


                    "eventExpressions": [{
                        "index": API.EVENT_EXPRESSION_INDEX,
                        "event": {
                            "index": API.CAMERA_EVENT_INDEX,
                            "params": Faker().first_name(),
                        },
                        "leftOperand": NullConstantsEnum.NULL_VALUE,
                        "operator": NullConstantsEnum.NULL_VALUE,
                        "rightOperand": NullConstantsEnum.NULL_VALUE,
                    }],

                    "criterionExpressions": [{
                        "grade": API.EVENT_EXPRESSION_INDEX,
                        "goal": API.EVENT_EXPRESSION_INDEX,
                        "index": API.CAMERA_EVENT_INDEX,
                        "criterion": {
                            "index": API.CAMERA_CRITERION_INDEX,
                            "params": Faker().first_name(),
                        },
                        "leftOperand": NullConstantsEnum.NULL_VALUE,
                        "operator": NullConstantsEnum.NULL_VALUE,
                        "rightOperand": NullConstantsEnum.NULL_VALUE,
                    }],
                    "publicTags": Faker().first_name(),
                    "privateTags": Faker().first_name(),
                },
            },
        }

        exercise_create_input = create_exercise_input["addExercise"]["exerciseCreateInput"]

        with aqas.step("Отправка запроса с мутацией <addExercise>"):
            exercise_data_actual = ApiGatewayAdapter().mutation("addExercise", create_exercise_input)

            actual_exercise_obj_camera = exercise_data_actual["exerciseObjects"][0]
            actual_exercise_obj_ipsc = exercise_data_actual["exerciseObjects"][1]
            TestsCrudExercise.EXERCISE_ID = exercise_data_actual["id"]
            TestsCrudExercise.OBJECT_ID_CAMERA = actual_exercise_obj_camera["id"]
            TestsCrudExercise.OBJECT_ID_IPSC = actual_exercise_obj_ipsc["id"]

        with aqas.step("Проверка типа"):
            assert all(isinstance(exercise_data_actual[key], str) for key in [
                "name", "sceneId", "status"]), "Не все поля типа str"
            assert isinstance(exercise_data_actual["deleted"], bool), "Ошибка тип не равен bool"

        with aqas.step("Проверить, что аргументы в ответе запроса соответствуют заданным аргументам при отправке"):
            dict_expected_exercise_data = update_dict_to_compare(exercise_create_input)
            comp_keys = ["name", "description", "sceneId", "deleted"]
            compare_dicts(dict_expected_exercise_data, exercise_data_actual, comp_keys)

            with aqas.step("""Проверить, что аргументы в ответе запроса соответствуют заданным аргументам
                       при отправке вложенного словаря environment"""):
                comp_keys = ["hitLimit", "timeLimit", "targetLimit", "scoreLimit",
                             "tracerEveryNShot", "season", "shooterPosition", "hour",
                             "precipitation", "visibility", "temperature", "pressure",
                             "windDirection", "windSpeed", "humidity", "altitude", "endOnWrongLane",
                             ]
                compare_dicts(dict_expected_exercise_data["environment"],
                              exercise_data_actual["environment"],
                              comp_keys,
                              )

            with aqas.step("""Проверить, что аргументы в ответе запроса соответствуют заданным аргументам
                       при отправке вложенного словаря exerciseObjects - camera"""):
                dict_expected_exercise_obj_camera = dict_expected_exercise_data["exerciseObjects"][0]
                dict_actual_exercise_obj_camera = update_dict_to_compare(actual_exercise_obj_camera)
                actual_exercise_commands_camera = dict_actual_exercise_obj_camera["exerciseCommands"][0]
                comp_keys = ["objectId", "name", "isCommandsCycled", "index", "position",
                             "rotation", "scale", "shotReactDistance", "targetType",
                             ]
                compare_dicts(dict_expected_exercise_obj_camera, dict_actual_exercise_obj_camera, comp_keys)

            assert (TestsCrudExercise.COMMAND_MOVE_ID == actual_exercise_commands_camera["commandId"]), (
                "Идентификатор команды не совпадает с заданным в запросе")

            assert (dict_expected_exercise_obj_camera["exerciseCommands"]["params"] == (
                actual_exercise_commands_camera["params"])), (
                "Параметры команды не совпадает с заданным в запросе")

            with aqas.step("""Проверить, что аргументы в ответе запроса соответствуют заданным аргументам
                       при отправке вложенного словаря exerciseObjects - Ipsc"""):
                dict_expected_exercise_obj_ipsc = dict_expected_exercise_data["exerciseObjects"][1]
                dict_actual_exercise_obj_ipsc = update_dict_to_compare(actual_exercise_obj_ipsc)
                comp_keys = ["objectId", "name", "isCommandsCycled", "index", "position",
                             "rotation", "scale", "shotReactDistance", "targetType",
                             ]
                compare_dicts(dict_expected_exercise_obj_ipsc, dict_actual_exercise_obj_ipsc, comp_keys)

            with aqas.step(
                    "Проверить, что аргументы exerciseWeaponPresets в ответе запроса соответствуют заданным"):
                assert API.WEAPON_ID_EX == exercise_data_actual["exerciseWeaponPresets"][0]["weaponTypeId"], (
                    "Параметры сущности для указания какие типы оружия доступны в упражнении "
                    "не совпадает с заданным в запросе")

                assert API.AMMO_ID_EX == exercise_data_actual["exerciseWeaponPresets"][0]["ammoTypeId"], (
                    "Параметры сущности для указания какие типы оружия доступны в упражнении "
                    "не совпадает с заданным в запросе")

            with aqas.step(
                    "Проверить, что аргументы eventExpressions в ответе запроса соответствуют заданным"):
                actual_event_expressions = exercise_data_actual["eventExpressions"][0]
                assert all(isinstance(actual_event_expressions[key], int) for key in [
                       "eventId", "id", "exerciseId"]), "Не все поля типа int"
                assert actual_event_expressions["index"] == API.EVENT_EXPRESSION_INDEX, (
                    "Индекс события в упражнении не совпадает с заданным в запросе")
                assert exercise_data_actual["id"] == actual_event_expressions["exerciseId"], (
                    "Не совпадает id упражнения в событии")

            with aqas.step("Проверить, что аргументы criterionExpressions в ответе запроса соответствуют заданным"):
                actual_criterion_expressions = exercise_data_actual["criterionExpressions"][0]
                expected_criterion_expressions = dict_expected_exercise_data["criterionExpressions"][0]
                comp_keys = ["index", "grade", "goal"]
                compare_dicts(expected_criterion_expressions, actual_criterion_expressions, comp_keys)

    @pytest.mark.dependency(depends=["test_create_exercise"], scope="class")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-405")
    @allure.title("update_exercise")
    def test_update_exercise(self):      # noqa: CFQ001
        with aqas.step("Добавить тэг для упражнения"):
            create_tag_input = {
                "addTag": {
                    "tagCreateInput": {
                        "name": API.TAG_NAME,
                        "scope": TagScopesEnum.PUBLIC,
                    },
                },
            }
            with aqas.step("Отправка запроса с мутацией <addTag>"):
                create_tag = ApiGatewayAdapter().mutation("addTag", create_tag_input)
            with aqas.step("Сохранение полученных данных в переменные"):
                TestsCrudExercise.TAG_ID = create_tag["id"]

        update_exercise_input = {
            "updateExerciseByid": {
                "exerciseInput": {
                    "id": TestsCrudExercise.EXERCISE_ID,
                    "name": Faker().first_name(),
                    "description": Faker().first_name(),
                    "sceneId": API.SCENE_ID_SHOOTING_RANGE,
                    "environment": {
                        "endOnWrongLane": Faker().boolean(),
                        "exerciseId": TestsCrudExercise.EXERCISE_ID,
                        "timeLimit": choice(API.TIMELIMIT),
                        "season": SeasonEnum.WINTER,
                        "shooterPosition": ShooterPositionEnum.LAY,
                        "precipitation": PrecipitationEnum.MIDDLE,
                        "hour": Faker().pyfloat(min_value=0, max_value=23),
                        "visibility": Faker().pyfloat(min_value=1, max_value=4000),
                        "temperature": Faker().pyfloat(min_value=-50, max_value=50),
                        "pressure": Faker().pyfloat(min_value=700, max_value=800),
                        "windDirection": Faker().pyfloat(min_value=0, max_value=360),
                        "windSpeed": Faker().pyfloat(min_value=0, max_value=30),
                        "humidity": Faker().pyfloat(min_value=1, max_value=50),
                        "altitude": Faker().pyfloat(min_value=1, max_value=50),
                        "hitLimit": Faker().random_int(1, 10),
                        "targetLimit": Faker().random_int(1, 10),
                        "scoreLimit": Faker().random_int(1, 10),
                        "tracerEveryNShot": Faker().random_int(1, 10),
                    },
                    "type": ExTypeEnum.DUEL,
                    "exerciseObjects": [{
                        "id": TestsCrudExercise.OBJECT_ID_CAMERA,
                        "objectId": API.OBJECT_GUUD_CAMERA,
                        "name": API.OBJECT_NAME_CAMERA,
                        "isCommandsCycled": Faker().boolean(),
                        "index": API.OBJECT_INDEX_CAMERA,
                        "position": API.POSITION_CAMERA,
                        "rotation": API.ROTATION_CAMERA,
                        "scale": API.SCALE_CAMERA,
                        "shotReactDistance": Faker().pyfloat(min_value=1, max_value=800),
                        "targetType": TargetTypeEnum.FRIENDLY,
                        "exerciseCommands": [{
                            "id": TestsCrudExercise.OBJECT_ID_CAMERA,
                            "commandId": TestsCrudExercise.COMMAND_MOVE_ID,
                            "params": API.COMMANDS_PARAMS_CAMERA,
                            "index": API.OBJECT_INDEX_CAMERA,
                            "eventExpression": {
                                "index": API.EVENT_EXPRESSION_INDEX,
                                "event": NullConstantsEnum.NULL_VALUE,
                                "leftOperand": NullConstantsEnum.NULL_VALUE,
                                "operator": NullConstantsEnum.NULL_VALUE,
                                "rightOperand": NullConstantsEnum.NULL_VALUE,
                            },
                        }],
                    }, {
                        "id": TestsCrudExercise.OBJECT_ID_IPSC,
                        "objectId": API.OBJECT_GUUD_IPSC_5,
                        "name": API.OBJECT_NAME_IPSC_5,
                        "isCommandsCycled": Faker().boolean(),
                        "index": API.OBJECT_INDEX_IPSC_5,  # +
                        "position": API.POSITION_2_IPSC_5,
                        "rotation": API.ROTATION_IPSC_5,
                        "scale": API.SCALE_IPSC_5,
                        "shotReactDistance": Faker().pyfloat(min_value=1, max_value=800),
                        "targetType": TargetTypeEnum.NOTTARGET,
                        "exerciseCommands": [],
                    }],
                    "exerciseWeaponPresets": [{
                        "weaponTypeId": API.WEAPON_ID_EX,
                        "ammoTypeId": API.AMMO_ID_EX,
                        "exerciseId": API.EX_ID_SHOOTING_RANGE,
                    }],
                    "criterionExpressions": [{
                        "grade": API.EVENT_EXPRESSION_INDEX,
                        "goal": API.EVENT_EXPRESSION_INDEX,
                        "index": API.CAMERA_EVENT_INDEX,
                        "criterion": {
                            "index": API.CAMERA_CRITERION_INDEX,
                            "params": Faker().first_name(),
                        },
                        "leftOperand": NullConstantsEnum.NULL_VALUE,
                        "operator": NullConstantsEnum.NULL_VALUE,
                        "rightOperand": NullConstantsEnum.NULL_VALUE,
                    }],
                    "eventExpressions": [{
                        "index": API.EVENT_EXPRESSION_INDEX,
                        "event": {
                            "index": API.CAMERA_EVENT_INDEX,
                            "params": Faker().first_name(),
                        },
                        "leftOperand": NullConstantsEnum.NULL_VALUE,
                        "operator": NullConstantsEnum.NULL_VALUE,
                        "rightOperand": NullConstantsEnum.NULL_VALUE,

                    }],
                    "tags": [{
                        "name": API.TAG_NAME,
                        "scope": TagScopesEnum.PUBLIC,
                    }],
                },
            },
        }

        exercise_update_input = update_exercise_input["updateExerciseByid"]["exerciseInput"]
        with aqas.step("Отправка запроса с мутацией <updateExerciseById>"):
            exercise_data_actual = ApiGatewayAdapter().mutation("updateExerciseById", update_exercise_input)
            actual_exercise_obj_camera = exercise_data_actual["exerciseObjects"][0]
            actual_exercise_obj_ipsc = exercise_data_actual["exerciseObjects"][1]

        with aqas.step("Проверка типа"):
            assert all(isinstance(exercise_data_actual[key], str) for key in [
                "name", "sceneId", "status"]), "Не все поля типа str"
            assert isinstance(exercise_data_actual["deleted"], bool), "Ошибка тип не равен bool"

        with aqas.step("Проверка обновления. Аргументы в ответе соответствуют заданным аргументам при отправке"):
            dict_expected_exercise_data = update_dict_to_compare(exercise_update_input)
            comp_keys = ["name", "description", "sceneId", "type"]
            compare_dicts(dict_expected_exercise_data, exercise_data_actual, comp_keys)

            with aqas.step(
                    """Проверить, что аргументы в ответе запроса соответствуют c заданными аргументами
                       при отправке вложенного словаря exerciseObjects - camera"""):
                dict_expected_exercise_obj_camera = dict_expected_exercise_data["exerciseObjects"][0]
                dict_actual_exercise_obj_camera = update_dict_to_compare(actual_exercise_obj_camera)
                comp_keys = ["objectId", "name", "isCommandsCycled", "index", "position",
                             "rotation", "scale", "shotReactDistance", "targetType", "id",
                             ]
                compare_dicts(dict_expected_exercise_obj_camera, dict_actual_exercise_obj_camera, comp_keys)

            with aqas.step(
                    """Проверить, что аргументы в ответе запроса соответствуют c заданными аргументами
                       при отправке вложенного словаря exerciseObjects - ipsc"""):
                dict_expected_exercise_obj_ipsc = dict_expected_exercise_data["exerciseObjects"][1]
                dict_actual_exercise_obj_ipsc = update_dict_to_compare(actual_exercise_obj_ipsc)
                comp_keys = ["objectId", "name", "isCommandsCycled", "index", "position",
                             "rotation", "scale", "shotReactDistance", "targetType", "id",
                             ]
                compare_dicts(dict_expected_exercise_obj_ipsc, dict_actual_exercise_obj_ipsc, comp_keys)

            with aqas.step("""Проверить, что аргументы в ответе запроса соответствуют c заданными аргументами
                       при отправке вложенного словаря environment"""):
                comp_keys = ["hitLimit", "timeLimit", "targetLimit", "scoreLimit",
                             "tracerEveryNShot", "season", "shooterPosition", "hour",
                             "precipitation", "visibility", "temperature", "pressure",
                             "windDirection", "windSpeed", "humidity", "altitude", "endOnWrongLane",
                             ]
                compare_dicts(dict_expected_exercise_data["environment"],
                              exercise_data_actual["environment"],
                              comp_keys,
                              )
            with aqas.step("Проверить, что аргументы тэга в ответе запроса соответствуют заданным при отправке"):
                tag_actual = exercise_data_actual["tags"][0]
                assert tag_actual["scope"] == TagScopesEnum.PUBLIC.value, "Приватность тэга не совпадает с заданной"
                assert tag_actual["name"] == API.TAG_NAME, "Имя тэга не совпадает с с заданным"

            with aqas.step("Проверить, что аргументы exerciseWeaponPresets в ответе запроса соответствуют заданным"):
                assert API.WEAPON_ID_EX == exercise_data_actual["exerciseWeaponPresets"][0]["weaponTypeId"], (
                    "Параметры сущности для указания какие типы оружия доступны в упражнении "
                    "не совпадает с заданным в запросе")

                assert API.AMMO_ID_EX == exercise_data_actual["exerciseWeaponPresets"][0]["ammoTypeId"], (
                    "Параметры сущности для указания какие типы оружия доступны в упражнении "
                    "не совпадает с заданным в запросе")

            with aqas.step("Проверить, что аргументы eventExpressions в ответе запроса соответствуют заданным"):
                actual_event_expressions = exercise_data_actual["eventExpressions"][0]

                with aqas.step("Проверка типа"):
                    assert all(isinstance(actual_event_expressions[key], int) for key in [
                        "id", "exerciseId", "index"]), "Не все поля типа int"

                assert exercise_data_actual["id"] == actual_event_expressions["exerciseId"], (
                    "Не совпадает id упражнения в совокупности событий")

                assert API.EVENT_EXPRESSION_INDEX == actual_event_expressions["index"], (
                    "Не совпадают значения index в совокупности событий")

            with aqas.step("Проверить, что аргументы criterionExpressions в ответе запроса соответствуют заданным"):
                actual_criterion_expressions = exercise_data_actual["criterionExpressions"][0]
                expected_criterion_expressions = dict_expected_exercise_data["criterionExpressions"][0]
                comp_keys = ["index", "grade", "goal"]
                compare_dicts(expected_criterion_expressions, actual_criterion_expressions, comp_keys)

    @pytest.mark.dependency(depends=["test_create_exercise"], scope="class")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-408")
    @allure.title("delete_exercise")
    def test_delete_exercise(self):
        with aqas.step("Отправка запроса с мутацией <removeExerciseById>"):
            result = ApiGatewayAdapter().remove_exercise_by_id(int(TestsCrudExercise.EXERCISE_ID))
        with aqas.step("Проверка наличия ответа"):
            assert result == 1, "Упражнение не удалено"

    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-973")
    @allure.title("restore_exercise_by_id")
    def test_restore_exercise_by_id(self):
        result = ApiGatewayAdapter().restore_exercise_by_id(int(TestsCrudExercise.EXERCISE_ID))
        with aqas.step("Проверка наличия ответа"):
            assert result == 1, "Упражнение не восстановлено"
        with aqas.step("Удалить упражнение после восстановления"):
            result = ApiGatewayAdapter().remove_exercise_by_id(int(TestsCrudExercise.EXERCISE_ID))
        with aqas.step("Проверка наличия ответа"):
            assert result == 1, "Упражнение не удалено"

        with aqas.step("Удалить тэг"):
            with aqas.step("Отправка запроса с мутацией <removeTag>"):
                tag_input = {
                    "tagInput": {
                        "name": API.TAG_NAME,
                        "id": TestsCrudExercise.TAG_ID,
                    },
                }
                result = ApiGatewayAdapter().remove_tag(tag_input)
            with aqas.step("Проверка наличия ответа"):
                assert result == 1, "Тэг не удален"
