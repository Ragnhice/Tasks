# pylint: disable=too-many-statements


import time
from datetime import datetime, timezone

import allure
import aqas
import pytest
from faker import Faker

import utils.data_utils
from models.api.api_gateway_adapter import ApiGatewayAdapter
from models.ui.forms.lane1_control_form import Lane1ControlForm
from steps.auth_steps import get_auth_admin
from steps.common_steps import get_any_msg_from_redis, get_shot_msg_from_redis, send_shot_msg_to_redis, subscribe_redis
from utils.constants import Hunter3D
from utils.element_utils import is_located
from utils.enums import GradesEnum, ScreenSizeEnum, StateEnum, WeaponModeEnum


@allure.parent_suite("unity")
@allure.suite("JerboaExerciseSettings")
@allure.sub_suite("ExerciseEditorSettings")
class TestJerboaExerciseSettings:
    """
    Класс, который содержит действия тестов:
        -  в широком режиме с имитатором
        -  передачи данных из Jerboa в Unity3d, Redis, GQL API сервис, WebUI
        -  имитация отправки сообщения из Jerboa в Hunter3D по протоколу UDP с пакетом данных о выстреле
        -  проверки выполнения условий установленных в настройках редактора упражнения при его создании/ изменении
    """

    @pytest.fixture(scope="function")
    @allure.title("Фикстура: Установка настроек тира с 2 полосами для проверки условий в упражнении на 1 полосе")
    def prepare_exercise_api(self):  # noqa: CFQ001
        with aqas.pre_step("Подписаться на канал shootingMode"):
            message_from_redis, redis = subscribe_redis("shootingMode")

        with aqas.pre_step("Сменить режим работы тира на широкий экран c 1 полосой и типом оружия Лазерный имитатор"):
            set_shooting_mode_input = {
                "setShootingMode": {
                    "mode": {
                        "screenSize": ScreenSizeEnum.WIDE,
                        "laneCount": Hunter3D.TWO_LANES,
                        "weaponMode": WeaponModeEnum.IMITATORS,
                    },
                },
            }
        with aqas.pre_step("Отправить запрос с мутацией <setShootingMode>"):
            ApiGatewayAdapter().mutation("setShootingMode", set_shooting_mode_input)

        with aqas.pre_step("Получить сообщение от Redis о режиме оружия"):
            message_from_redis = get_any_msg_from_redis(message_from_redis, redis)

            assert message_from_redis["weaponMode"] == Hunter3D.TWO_LANES, (
                "Ошибка установки режима боевого оружия в данных канале Redis")

        with aqas.pre_step("Отправить запрос shootingMode на backend, проверить установленные значения"):
            shooting_mode = ApiGatewayAdapter().query("shootingMode")
            assert shooting_mode["screenSize"] == ScreenSizeEnum.WIDE.value, "Ошибка установки ширины экрана"
            assert shooting_mode["weaponMode"] == WeaponModeEnum.IMITATORS.value, "Ошибка установки оружия"
            time.sleep(Hunter3D.TWO_LANES)

        with aqas.pre_step("Отправить запрос shootingMode на backend, проверить установленные значения"):
            shooting_mode = ApiGatewayAdapter().query("shootingMode")
            assert shooting_mode["screenSize"] == ScreenSizeEnum.WIDE.value, "Ошибка установки ширины экрана"
            assert shooting_mode["weaponMode"] == WeaponModeEnum.IMITATORS.value, "Ошибка установки режима оружия"

        with aqas.pre_step("Занять полосу"):
            set_instructor_to_lane_input = {
                "setInstructorToLane": {
                    "instructorId": Hunter3D.ADMIN_ID,
                    "laneNumbers": [1, 2],
                },
            }
            with aqas.pre_step("Отправить запроса с мутацией <setInstructorToLane>"):
                instructor_to_lane = ApiGatewayAdapter().mutation("setInstructorToLane",
                                                                  set_instructor_to_lane_input)
            with aqas.pre_step("Проверить номера полосы"):
                assert instructor_to_lane[0]["laneNumber"] == 1, "Ошибка номера полосы"
                assert instructor_to_lane[1]["laneNumber"] == 2, "Ошибка номера полосы"

        with aqas.pre_step("Подписаться на канал exercise"):
            message_from_redis, redis = subscribe_redis("exercise")

        with aqas.pre_step("Установить упражнение на 1 полосе"):
            set_ex_to_lane_input = {
                "setExerciseToLane": {
                    "exerciseId": Hunter3D.EX_ID,
                    "laneNumber": 1,
                },
            }
            with aqas.pre_step("Отправить запрос с мутацией <setExerciseToLane>"):
                ex_to_lane = ApiGatewayAdapter().mutation("setExerciseToLane", set_ex_to_lane_input)
            with aqas.pre_step("Проверить номера полосы"):
                assert ex_to_lane["laneNumber"] == 1, "Ошибка номера полосы"
                assert ex_to_lane["exerciseId"] == Hunter3D.EX_ID, "Ошибка id упражнения"

        with aqas.pre_step("Получить сообщение от Redis c номером упражнения на полосе"):
            message_from_redis = get_any_msg_from_redis(message_from_redis, redis)

            assert message_from_redis["exercise"]["id"] == Hunter3D.EX_ID, (
                "Ошибка установки упражнения в данных канале Redis")

        with aqas.pre_step("Подписаться на канал exercise"):
            message_from_redis, redis = subscribe_redis("exercise")

        with aqas.pre_step("Установить упражнение на 2 полосе"):
            set_ex_to_lane_input = {
                "setExerciseToLane": {
                    "exerciseId": Hunter3D.EX_ID,
                    "laneNumber": 2,
                },
            }
            with aqas.pre_step("Отправить запрос с мутацией <setExerciseToLane>"):
                ex_to_lane = ApiGatewayAdapter().mutation("setExerciseToLane", set_ex_to_lane_input)
            with aqas.pre_step("Проверить номера полосы"):
                assert ex_to_lane["laneNumber"] == 2, "Ошибка номера полосы"
                assert ex_to_lane["exerciseId"] == Hunter3D.EX_ID, "Ошибка id упражнения"

        with aqas.pre_step("Получить сообщение от Redis c номером упражнения на полосе"):
            message_from_redis = get_any_msg_from_redis(message_from_redis, redis)

            assert message_from_redis["exercise"]["id"] == Hunter3D.EX_ID, (
                "Ошибка установки упражнения в данных канале Redis")

        time.sleep(Hunter3D.TIMEOUT_HUNTER3D_SETTINGS)

        with aqas.pre_step("Установить на 1 полосу стрелка c оружием"):
            set_shooter_to_lane_input = {
                "setShootersToLane": {
                    "shooterInputs": [{
                        "userId": Hunter3D.SHOOTER_ID,
                        "weaponInputs": [{
                            "weaponId": Hunter3D.WEAPON_AK74_ID,
                            "ammoTypeId": Hunter3D.AMMO_TYPE_AK74_ID,
                            "magazines": [Faker().random_int(5, 10)],
                        }],
                    }],
                    "laneNumber": 1,
                },
            }
            with aqas.pre_step("Отправить запрос с мутацией <setShootersToLane>"):
                shooter_to_lane = ApiGatewayAdapter().mutation("setShootersToLane", set_shooter_to_lane_input)
            with aqas.pre_step("Проверить номера полосы"):
                assert shooter_to_lane["laneNumber"] == 1, "Ошибка номера полосы"
            with aqas.pre_step("Проверить номера упражнения"):
                assert shooter_to_lane["exerciseId"] == Hunter3D.EX_ID, "Ошибка в номере упражнения"

        with aqas.pre_step("Пройти аутентификацию администратором и перейти на страницу управления полосами"):
            lanes_control_page = get_auth_admin()

        with aqas.pre_step("Перейти на страницу управления 1 полосой"):
            lanes_control_page.elements.LANE1_LBL.wait_and_click()
            lane1_control_page = Lane1ControlForm()
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            assert lane1_control_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.pre_step("Запустить упражнение"):
            set_state_to_lane_input = {
                "setStateToLane": {
                    "state": StateEnum.START,
                    "laneNumber": 1,
                },
            }
            with aqas.pre_step("Отправить запрос с мутацией <setStateToLane>"):
                state_to_lane = ApiGatewayAdapter().mutation("setStateToLane", set_state_to_lane_input)
            with aqas.pre_step("Проверить типа"):
                assert state_to_lane["laneNumber"] == 1, "Ошибка номера полосы"

            with aqas.pre_step("Получить сообщение от Redis о статусе полосы"):
                aqas.wait_until(
                    method=lambda: (
                        get_shot_msg_from_redis("stateChanged")["sessionState"] == Hunter3D.REDIS_SESSION_STATE_START),
                    message="Упражнение не запустилось",
                )

        yield lane1_control_page

        with aqas.post_step("Сменить режим работы тира на широкий экран c типом оружия Лазерный имитатор"):
            set_shooting_mode_input = {
                "setShootingMode": {
                    "mode": {
                        "screenSize": ScreenSizeEnum.WIDE,
                        "laneCount": Faker().random_int(1, 5),
                        "weaponMode": WeaponModeEnum.IMITATORS,
                    },
                },
            }
        with aqas.post_step("Отправить запроса с мутацией <setShootingMode>"):
            ApiGatewayAdapter().mutation("setShootingMode", set_shooting_mode_input)

        with aqas.post_step("Отправить запрос shootingMode на backend, проверить установленных значений"):
            shooting_mode = ApiGatewayAdapter().query("shootingMode")
            assert shooting_mode["screenSize"] == ScreenSizeEnum.WIDE.value, "Ошибка установки ширины экрана"
            assert shooting_mode["weaponMode"] == WeaponModeEnum.IMITATORS.value, "Ошибка установки режима оружия"

        with aqas.post_step("Добавить стрелка без оружия"):
            set_shooter_to_lane_input = {
                "setShootersToLane": {
                    "shooterInputs": [{
                        "userId": Hunter3D.SHOOTER_ID,
                        "weaponInputs": [],
                    }],
                    "laneNumber": 1,
                },
            }
            with aqas.post_step("Отправить запрос с мутацией <setShootersToLane>"):
                shooter_to_lane = ApiGatewayAdapter().mutation("setShootersToLane", set_shooter_to_lane_input)
            with aqas.post_step("Проверить номера полосы"):
                assert shooter_to_lane["laneNumber"] == 1, "Ошибка номера полосы"
            with aqas.post_step("Проверить типа"):
                assert not shooter_to_lane["isBusy"], "Ошибка, статуса полосы Занята"

    @pytest.mark.usefixtures("start_browser")
    @allure.title("shot_wrong_lane_imitator")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-1217")
    def test_shot_wrong_lane_imitator(self, prepare_exercise_api):  # noqa: CFQ001
        """
        Проверка передачи данных о выстреле не в свою полосу из имитатора с широким размером экрана
        по протоколу UDP из Jerboa в Unity-Hunter3d,после в Redis,
        далее в GQL HunterAPI сервис и в WebUI с данными о выстреле и об окончании упражнения.
        """
        lane1_control_page = prepare_exercise_api

        with aqas.step("1. Сохранить HWID установленного оружия"):
            weapon_hwid = aqas.wait_until(
                method=ApiGatewayAdapter().check_hwid,
                ignored_exceptions=[AssertionError],
                message="Тип для поля 'hwid' не равен int",
            )

        with aqas.step("2. Сформировать сообщение о точке промаха"):
            miss_point_message = utils.data_utils.encode_imitators_point_message(
                weapon_hwid, Hunter3D.POINTX_MISS_TWO_LANES, Hunter3D.POINTY_MISS)

        with aqas.step("3. Сформировать сообщение о выстреле с промахом"):
            miss_shot_message = utils.data_utils.encode_imitators_shot_message(
                weapon_hwid)

        with aqas.step("4. Получить сообщение от Redis о выстреле с промахом"):
            message_from_redis = get_shot_msg_from_redis("shot", miss_point_message, miss_shot_message)

        with aqas.step("5. Получить данные из API для сравнения с данными в канале Redis"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")[0]["shooting"][0]

        with aqas.step("6. Проверить наличие данных о выстреле с промахом сообщения от Redis по ключу shot"):
            assert message_from_redis["LaneNumber"] == Hunter3D.FIRST_LANE, (
                "В данных сообщения о выстреле не зафиксирована полоса")
            assert not message_from_redis["IsHitted"], (
                "В данных сообщения о выстреле c промахом зафиксировано попадание")
            assert message_from_redis["Score"] == Hunter3D.SCORE_REDIS_ONE_MISS, (
                "В данных сообщения очки не соответствуют промаху")
            assert message_from_redis["TargetId"] == Hunter3D.TARGET_MISS, (
                "В данных сообщения о выстреле зафиксирован id цели")
            assert message_from_redis["PrefabName"] == lane_datas["prefabName"], (
                "В данных сообщения о выстреле c промахом зафиксировано Наименование префаба")
            assert message_from_redis["Score"] == lane_datas["score"], (
                "В данных сообщения о выстреле c промахом зафиксированы Баллы")
            assert message_from_redis["HitZoneName"] == lane_datas["hitZoneName"], (
                "В данных сообщения о выстреле c промахом зафиксировано Наименование зоны попадания")
            assert message_from_redis["IsHitted"] == lane_datas["isHitted"], (
                "В данных сообщения о выстреле c промахом зафиксирован неверный Результат")

        with aqas.step("7. Проверить передачу статистики из HunterAPI в WebUI и заполнения таблицы"):
            aqas.wait_until(
                method=lambda: int(
                    lane1_control_page.elements.NUMBER_OF_SHOTS_LBL.text) == Hunter3D.NUMBER_SHOTS_ONE_MISS,
                timeout=30,
                message="Ошибка, выстрелы не появились в UI",
            )
            assert int(lane1_control_page.elements.SCORE_LBL.text) == Hunter3D.SCORE_UI_ONE_MISS, (
                "Ошибка, очки не зафиксированы в UI")
            assert int(lane1_control_page.elements.NUMBER_OF_HITS_LBL.text) == Hunter3D.NUMBER_HITS_ONE_MISS, (
                "Ошибка, промах не зафиксирован в UI")

        with aqas.step("8. Сформировать сообщение о точке на чужой (№2) полосе"):
            miss_point_message = utils.data_utils.encode_imitators_point_message(
                weapon_hwid, Hunter3D.POINTX_WRONG_LANE_TWO_LANES, Hunter3D.POINTY_WRONG_LANE_TWO_LANES)

        with aqas.step("9. Сформировать сообщение о точке выстрела по чужой полосе"):
            miss_shot_message = utils.data_utils.encode_imitators_shot_message(
                weapon_hwid)

        with aqas.pre_step("10. Подписаться на канал shot"):
            subscribe_redis("shot")

        with aqas.step("11. Отправить сообщение о выстреле по чужой полосе"):
            send_shot_msg_to_redis("shot", miss_point_message, miss_shot_message)

        with aqas.step("12. Проверить сохранение статистики в WebUI"):
            aqas.wait_until(
                method=lambda: int(
                    lane1_control_page.elements.NUMBER_OF_SHOTS_LBL.text) == Hunter3D.NUMBER_SHOTS_ONE_MISS,
                message="Ошибка, статистика поменялась в UI",
            )
            assert int(lane1_control_page.elements.SCORE_LBL.text) == Hunter3D.SCORE_UI_ONE_MISS, (
                "Ошибка, очки не зафиксированы в UI")
            assert int(lane1_control_page.elements.NUMBER_OF_HITS_LBL.text) == Hunter3D.NUMBER_HITS_ONE_MISS, (
                "Ошибка, промах не зафиксирован в UI")

        with aqas.step("13. Проверить c UI, что упражнение остановилось"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            assert is_located(lane1_control_page.elements.STOP_DISABLED_LBL), "Ошибка, упражнение не остановилось в UI"

        with aqas.step("14. Проверить совпадение заданного статуса полосы с UI со значением с backend"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["sessionState"] == StateEnum.STOP.value,
                message="Ошибка, упражнение не остановилось",
            )

        with aqas.step("15. Сделать GraphQL запрос exercisesStatistic"):
            exercises_statistic = ApiGatewayAdapter().query("exercisesStatistic")[-1]

        with aqas.step("16. Проверить наличие ответа"):
            assert exercises_statistic["exerciseType"], "Нет ответа от запроса"

        with aqas.step("17. Проверить информации об имени завершенного упражнения"):
            assert exercises_statistic["exerciseName"] == Hunter3D.EX_NAME_JERBOA, (
                "Ошибка,  имя упр. в сервисе не зафиксировано")

        with aqas.step("18. Проверить информацию о дате в завершенном упражнении"):
            assert str(datetime.now(timezone.utc)).split()[0] in exercises_statistic["dateTime"], (
                "Ошибка, дата в сервисе не зафиксирована")

        with aqas.step("19. Проверить информацию о выстрелах, совершенных в завершенном упражнении"):
            assert exercises_statistic["numberOfShots"] == Hunter3D.NUMBER_SHOTS_ONE_MISS, (
                "Ошибка, выстрелы не зафиксированы в сервисе")

        with aqas.step("20. Проверить информации об очках в завершенном упражнении"):
            assert exercises_statistic["score"] == Hunter3D.SCORE_UI_ONE_MISS, (
                "Ошибка, очки не зафиксированы в сервисе")

    @pytest.mark.usefixtures("start_browser")
    @allure.title("bad_grade_in_redis")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-1329")
    def test_bad_grade_in_redis(self, prepare_exercise_api):
        """
        Проверка передачи данных после завершения упражнения в Redis канал
        о неудовлетворительной оценке с критерием ее выставления при промахе.
        """

        with aqas.step("1. Сохранить HWID установленного оружия"):
            weapon_hwid = aqas.wait_until(
                method=ApiGatewayAdapter().check_hwid,
                ignored_exceptions=[AssertionError],
                message="Тип для поля 'hwid' не равен int",
            )

        with aqas.step("2. Сформировать сообщение о точке промаха"):
            miss_point_message = utils.data_utils.encode_imitators_point_message(
                weapon_hwid, Hunter3D.POINTX_MISS_TWO_LANES, Hunter3D.POINTY_MISS)

        with aqas.step("3. Сформировать сообщение о выстреле с промахом"):
            miss_shot_message = utils.data_utils.encode_imitators_shot_message(
                weapon_hwid)

        with aqas.pre_step("4. Подписаться на канал exerciseGrade"):
            message_from_redis, redis = subscribe_redis("exerciseGrade")

        with aqas.step("5. Отправить сообщение о выстреле c промахом"):
            send_shot_msg_to_redis("shot", miss_point_message, miss_shot_message)

        with aqas.step("6. Остановить упражнение"):
            set_state_to_lane_input = {
                "setStateToLane": {
                    "state": StateEnum.STOP,
                    "laneNumber": 1,
                },
            }
            with aqas.step("Отправка запроса с мутацией <setStateToLane>"):
                state_to_lane = ApiGatewayAdapter().mutation("setStateToLane", set_state_to_lane_input)
            with aqas.step("Проверить, что аргументы в ответе соответствуют аргументам запроса"):
                assert (state_to_lane["laneNumber"] == set_state_to_lane_input["setStateToLane"]["laneNumber"]), (
                    "Аргумент номера полосы не совпадает")
                assert (state_to_lane["sessionState"] == set_state_to_lane_input["setStateToLane"]["state"].value), (
                    "Аргумент статуса полосы не совпадают")

        with aqas.pre_step("7. Получить сообщение в Redis канале c оценкой на полосе"):
            message_from_redis = get_any_msg_from_redis(message_from_redis, redis)
            assert message_from_redis["Grade"] == GradesEnum.GRADE_TWO.value, (
                "Ошибка выставления оценки 'Неуд' в данных канала в Redis")

        with aqas.step("8. Сделать GraphQL запрос exercisesStatistic"):
            exercises_statistic = ApiGatewayAdapter().query("exercisesStatistic")[-1]
            assert exercises_statistic["exerciseType"], "Нет ответа от запроса"

        with aqas.step("9. Проверить информацию об имени завершенного упражнения"):
            assert exercises_statistic["exerciseName"] == Hunter3D.EX_NAME_JERBOA, (
                "Ошибка,  имя упр. в API сервиса не зафиксировано")

        with aqas.step("10. Проверить информацию о дате в завершенном упражнении"):
            assert str(datetime.now(timezone.utc)).split()[0] in exercises_statistic["dateTime"], (
                "Ошибка, дата в API сервиса не зафиксирована")

        with aqas.step("11. Проверить информацию об очках в завершенном упражнении"):
            assert exercises_statistic["score"] == Hunter3D.SCORE_UI_ONE_MISS, (
                "Ошибка, очки не зафиксированы в сервисе")
