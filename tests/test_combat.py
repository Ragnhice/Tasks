# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
import time
from datetime import datetime, timezone

import allure
import aqas
import pytest
from faker import Faker

import utils.data_utils
from models.api.api_gateway_adapter import ApiGatewayAdapter
from models.ui.forms.lane1_control_form import Lane1ControlForm
from models.ui.forms.alert_form import AlertForm
from steps.auth_steps import get_auth_admin
from steps.common_steps import get_any_msg_from_redis, get_shot_msg_from_redis, subscribe_redis
from utils.constants import Hunter3D
from utils.element_utils import is_located
from utils.enums import ScreenSizeEnum, StateEnum, WeaponModeEnum


@allure.parent_suite("unity")
@allure.suite("JerboaCombat")
class TestJerboaCombat:
    """
    Класс, который содержит действия тестов в широком режиме с боевым типом оружия:
        -  передачи данных из Jerboa в Unity3d, Redis, GQL API сервис
        -  заполнения данными о выстрелах таблицы в WebUI путем имитации отправки сообщения
           из Jerboa в Hunter3D по протоколу UDP с пакетом данных о выстреле

    """
    @pytest.fixture()
    def prepare_exercise_api(self):  # noqa: CFQ001

        with aqas.pre_step("Подписаться на канал shootingMode"):
            message_from_redis, redis = subscribe_redis("shootingMode")

        with aqas.pre_step("Сменить режим работы тира на широкий экран c 1 полосой и с Боевым типом оружия>"):
            set_shooting_mode_input = {
                "setShootingMode": {
                    "mode": {
                        "screenSize": ScreenSizeEnum.WIDE,
                        "laneCount": Hunter3D.FIRST_LANE,
                        "weaponMode": WeaponModeEnum.COMBAT,
                    },
                },
            }
        with aqas.step("Отправка запроса с мутацией <setShootingMode>"):
            ApiGatewayAdapter().mutation("setShootingMode", set_shooting_mode_input)

        with aqas.step("Получить сообщение от Redis о режиме оружия"):
            message_from_redis = get_any_msg_from_redis(message_from_redis, redis)

            assert message_from_redis["weaponMode"] == Hunter3D.WEAPON_MODE_COMBAT, (
                "Ошибка установки режима боевого оружия в данных в канале Redis")
            time.sleep(Hunter3D.TIMEOUT_HUNTER3D_SETTINGS)

        with aqas.pre_step("Отправка запроса shootingMode на backend, проверка установленных значений"):
            shooting_mode = ApiGatewayAdapter().query("shootingMode")
            assert shooting_mode["screenSize"] == ScreenSizeEnum.WIDE.value, "Ошибка установки ширины экрана"
            assert shooting_mode["weaponMode"] == WeaponModeEnum.COMBAT.value, "Ошибка установки режима оружия"
            assert shooting_mode["laneCount"] == Hunter3D.FIRST_LANE, "Ошибка установки количества полос"

        with aqas.pre_step("Занять полосу"):
            set_instructor_to_lane_input = {
                "setInstructorToLane": {
                    "instructorId": Hunter3D.ADMIN_ID,
                    "laneNumbers": [1],
                },
            }
            with aqas.step("Отправка запроса с мутацией <setInstructorToLane>"):
                instructor_to_lane = ApiGatewayAdapter().mutation("setInstructorToLane",
                                                                  set_instructor_to_lane_input)
            with aqas.step("Проверка номера полосы"):
                assert instructor_to_lane[0]["laneNumber"] == 1, "Ошибка номера полосы"

        with aqas.pre_step("Подписаться на канал exercise"):
            message_from_redis, redis = subscribe_redis("exercise")

        with aqas.pre_step("Установить упражнение"):
            set_ex_to_lane_input = {
                "setExerciseToLane": {
                    "exerciseId": Hunter3D.EX_ID,
                    "laneNumber": 1,
                },
            }
            with aqas.step("Отправка запроса с мутацией <setExerciseToLane>"):
                ex_to_lane = ApiGatewayAdapter().mutation("setExerciseToLane", set_ex_to_lane_input)
            with aqas.step("Проверка номера полосы"):
                assert ex_to_lane["laneNumber"] == 1, "Ошибка номера полосы"
                assert ex_to_lane["exerciseId"] == Hunter3D.EX_ID, "Ошибка id упражнения"

        with aqas.step("Получить сообщение от Redis c номером упражнения на полосе"):
            message_from_redis = get_any_msg_from_redis(message_from_redis, redis)

            assert message_from_redis["exercise"]["id"] == Hunter3D.EX_ID, (
                "Ошибка установки упражнения в данных канале Redis")

        with aqas.step("Установить на полосу стрелка c оружием"):
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
            with aqas.step("Отправка запроса с мутацией <setShootersToLane>"):
                shooter_to_lane = ApiGatewayAdapter().mutation("setShootersToLane", set_shooter_to_lane_input)
            with aqas.step("Проверка номера полосы"):
                assert shooter_to_lane["laneNumber"] == 1, "Ошибка номера полосы"
            with aqas.step("Проверка номера упражнения"):
                assert shooter_to_lane["exerciseId"] == Hunter3D.EX_ID, "Ошибка в номере упражнения"
            time.sleep(Hunter3D.TIMEOUT_HUNTER3D_SETTINGS)

        with aqas.pre_step("Аутентификация администратором и переход на страницу управления полосами"):
            lanes_control_page = get_auth_admin()

        with aqas.pre_step("Переход на страницу управления 1 полосой"):
            lanes_control_page.elements.LANE1_LBL.wait_and_click()
            lane1_control_page = Lane1ControlForm()
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            assert lane1_control_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.pre_step("Запуск упражнения"):
            set_state_to_lane_input = {
                "setStateToLane": {
                    "state": StateEnum.START,
                    "laneNumber": 1,
                },
            }
            with aqas.step("Отправка запроса с мутацией <setStateToLane>"):
                state_to_lane = ApiGatewayAdapter().mutation("setStateToLane", set_state_to_lane_input)
            with aqas.step("Проверка типа"):
                assert state_to_lane["laneNumber"] == 1, "Ошибка номера полосы"

        with aqas.step("Получить сообщение от Redis о статусе полосы"):
            aqas.wait_until(
                method=lambda: (
                    get_shot_msg_from_redis("stateChanged")["sessionState"] == Hunter3D.REDIS_SESSION_STATE_START),
                message="Упражнение не запустилось",
            )

        yield lane1_control_page

        with aqas.pre_step("Сменить режим работы тира на широкий экран c 1 полосой и типом оружия Лазерный имитатор"):
            set_shooting_mode_input = {
                "setShootingMode": {
                    "mode": {
                        "screenSize": ScreenSizeEnum.WIDE,
                        "laneCount": Faker().random_int(1, 5),
                        "weaponMode": WeaponModeEnum.IMITATORS,
                    },
                },
            }
        with aqas.step("Отправка запроса с мутацией <setShootingMode>"):
            ApiGatewayAdapter().mutation("setShootingMode", set_shooting_mode_input)

        with aqas.pre_step("Отправка запроса shootingMode на backend, проверка установленных значений"):
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
            with aqas.step("Отправка запроса с мутацией <setShootersToLane>"):
                shooter_to_lane = ApiGatewayAdapter().mutation("setShootersToLane", set_shooter_to_lane_input)
            with aqas.step("Проверка номера полосы"):
                assert shooter_to_lane["laneNumber"] == 1, "Ошибка номера полосы"
            with aqas.step("Проверка типа"):
                assert not shooter_to_lane["isBusy"], "Ошибка, статуса полосы Занята"

    @pytest.mark.usefixtures("start_browser")
    @allure.title("jerboa_combat_miss")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-671")
    def test_jearboa_combat_miss(self, prepare_exercise_api):  # noqa: CFQ001
        """
        Проверка передачи данных о выстреле из боевого оружия с широким размером экрана
        с промахом по протоколу UDP из Jerboa в Unity-Hunter3d,
        после в Redis, далее в GQL HunterAPI сервис и в WebUI с заполнением таблицы данными о выстреле
        """
        lane1_control_page = prepare_exercise_api

        with aqas.step("Сохранить HWID установленного оружия"):
            aqas.wait_until(
                method=lambda: isinstance(
                    ApiGatewayAdapter().query("laneDatas")[0]["shooters"][0]["weapons"][0]["hwid"], int),
                message="Нет значения hwid в ответе запроса laneDatas",
            )
            weapon_hwid = ApiGatewayAdapter().query("laneDatas")[0]["shooters"][0]["weapons"][0]["hwid"]

        with aqas.step("Формирования сообщение о выстреле, где есть промах"):
            miss_shot_message = utils.data_utils.encode_lightweight_combat_shot_message(
                weapon_hwid, Hunter3D.POINTX_MISS, Hunter3D.POINTY_MISS)

        with aqas.step("Получить сообщение от Redis о выстреле"):
            message_from_redis = get_shot_msg_from_redis("shot", miss_shot_message)

        with aqas.step("Получить данные из API для сравнения с данными в канале Redis"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")[0]["shooting"][0]

        with aqas.step("Проверка наличия данных о выстреле с промахом сообщения от Redis по ключу shot"):
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
            assert not message_from_redis["IsHitted"], (
                "В данных сообщения о выстреле c промахом зафиксирован неверный Результат")

        with aqas.step("Проверка передачи статистики из HunterAPI в WebUI и заполнения таблицы"):
            aqas.wait_until(
                method=lambda: int(
                    lane1_control_page.elements.NUMBER_OF_SHOTS_LBL.text) == Hunter3D.NUMBER_SHOTS_ONE_MISS,
                timeout=30,
                message="Ошибка, выстрелы не появились в UI",
            )
            assert int(lane1_control_page.elements.SCORE_LBL.text) == Hunter3D.SCORE_UI_ONE_MISS, (
                "Ошибка, очки не зафиксированы в UI")
            assert int(lane1_control_page.elements.NUMBER_OF_HITS_LBL.text) == Hunter3D.NUMBER_HITS_ONE_MISS, (
                "Ошибка, попадания не зафиксированы в UI")

        with aqas.step("Остановить упражнение"):
            if not is_located(lane1_control_page.elements.STOP_DISABLED_LBL):
                lane1_control_page.elements.STOP_BTN.click()

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert = AlertForm()
            if is_located(alert.elements.NOTIFICATIONS_FORM):
                alert.wait_for_notifications_invisible()

        with aqas.step("Проверка совпадения заданного статуса полосы  с UI со значением с backend"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["sessionState"] == StateEnum.STOP.value,
                message="Ошибка, упражнение не остановилось",
            )

        with aqas.step("Сделать GraphQL запрос exercisesStatistic"):
            exercises_statistic = ApiGatewayAdapter().query("exercisesStatistic")[-1]

        with aqas.step("Проверка наличия ответа"):
            assert exercises_statistic["exerciseType"], "Нет ответа от запроса"

        with aqas.step("Проверка информации об имени завершенного упражнения"):
            assert exercises_statistic["exerciseName"] == Hunter3D.EX_NAME_JERBOA, (
                "Ошибка,  имя упр. в сервисе не зафиксировано")

        with aqas.step("Проверка информации о дате в завершенном упражнении"):
            assert str(datetime.now(timezone.utc)).split()[0] in exercises_statistic["dateTime"], (
                "Ошибка, дата в сервисе не зафиксирована")

        with aqas.step("Проверка информации о выстрелах, совершенных в завершенном упражнении"):
            assert exercises_statistic["numberOfShots"] == Hunter3D.NUMBER_SHOTS_ONE_MISS, (
                "Ошибка, выстрелы не зафиксированы в сервисе")

        with aqas.step("Проверка информации Проверка информации об очках в завершенном упражнении"):
            assert exercises_statistic["score"] == Hunter3D.SCORE_UI_ONE_MISS, (
                "Ошибка, очки не зафиксированы в сервисе")

    @pytest.mark.usefixtures("start_browser")
    @allure.title("jearboa_combat_hit")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-670")
    def test_jearboa_combat_hit(self, prepare_exercise_api):  # noqa: CFQ001
        """
        Проверка передачи данных о выстреле из боевого оружия с широким размером экрана
        с попаданием по протоколу UDP из Jerboa в Unity-Hunter3d,
        после в Redis, далее в GQL HunterAPI сервис и в WebUI с заполнением данными о выстреле таблицы
        """
        lane1_control_page = prepare_exercise_api

        with aqas.step("Сохранить HWID установленного оружия"):
            aqas.wait_until(
                method=lambda: isinstance(
                    ApiGatewayAdapter().query("laneDatas")[0]["shooters"][0]["weapons"][0]["hwid"], int),
                message="Нет значения hwid в ответе запроса laneDatas",
            )
            weapon_hwid = ApiGatewayAdapter().query("laneDatas")[0]["shooters"][0]["weapons"][0]["hwid"]

        with aqas.step("Формирования сообщение о выстреле, где есть попадание"):
            hit_shot_message = utils.data_utils.encode_lightweight_combat_shot_message(
                weapon_hwid, Hunter3D.POINTX_HIT, Hunter3D.POINTY_HIT)

        with aqas.step("Получить сообщение от Redis о выстреле"):
            message_from_redis = get_shot_msg_from_redis("shot", hit_shot_message)

        with aqas.step("Получить данные из API для сравнения с данными в канале Redis"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")[0]["shooting"][0]

        with aqas.step("Проверка наличия данных о выстреле с попаданием в сообщении от Redis по ключу shot"):
            assert message_from_redis["LaneNumber"] == Hunter3D.FIRST_LANE, (
                "В данных сообщения о выстреле не зафиксирована полоса")
            assert message_from_redis["IsHitted"], (
                "В данных сообщения о выстреле не зафиксировано попадание")
            assert message_from_redis["Score"] == Hunter3D.SCORE_REDIS_ONE_HIT, (
                "В данных сообщения о выстреле не зафиксированы очки попадания")
            assert str(message_from_redis["PrefabName"]) == str(lane_datas["prefabName"]), (
                "В данных сообщения о выстреле Наименование префаба не совпадает со значением в API")
            assert int(message_from_redis["Score"]) == lane_datas["score"], (
                "В данных сообщения о выстреле Баллы  не совпадают со значением в API")
            assert message_from_redis["HitZoneName"] == lane_datas["hitZoneName"], (
                "В данных сообщения о выстреле Наименование зоны попадания не совпадает со значением в API")
            assert message_from_redis["TargetId"] == lane_datas["targetId"], (
                "В данных сообщения о выстреле Результат попадания не совпадает со значением в API")

        with aqas.step("Проверка передачи статистики из HunterAPI в WebUI и заполнения таблицы"):
            aqas.wait_until(
                method=lambda: int(
                    lane1_control_page.elements.NUMBER_OF_SHOTS_LBL.text) == Hunter3D.NUMBER_SHOTS_ONE_HIT,
                timeout=30,
                message="Ошибка, выстрелы не появились в UI",
            )
            assert int(lane1_control_page.elements.SCORE_LBL.text) == Hunter3D.SCORE_UI_ONE_HIT, (
                "Ошибка, очки не зафиксированы в UI")
            assert int(lane1_control_page.elements.NUMBER_OF_HITS_LBL.text) == Hunter3D.NUMBER_HITS_ONE_HIT, (
                "Ошибка,  попадания не зафиксированы в UI")

        with aqas.step("Остановить упражнение"):
            if not is_located(lane1_control_page.elements.STOP_DISABLED_LBL):
                lane1_control_page.elements.STOP_BTN.click()

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert = AlertForm()
            if is_located(alert.elements.NOTIFICATIONS_FORM):
                alert.wait_for_notifications_invisible()

        with aqas.step("Проверка совпадения заданного статуса полосы  с UI со значением с backend"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["sessionState"] == StateEnum.STOP.value,
                message="Ошибка, упражнение не остановилось",
            )

        with aqas.step("Сделать GraphQL запрос exercisesStatistic"):
            exercises_statistic = ApiGatewayAdapter().query("exercisesStatistic")[-1]

        with aqas.step("Проверка наличия ответа"):
            assert exercises_statistic["exerciseType"], "Нет ответа от запроса"

        with aqas.step("Проверка информации об имени завершенного упражнения"):
            assert exercises_statistic["exerciseName"] == Hunter3D.EX_NAME_JERBOA, (
                "Ошибка, имя упр. в сервисе не зафиксировано")

        with aqas.step("Проверка информации о дате в завершенном упражнении"):
            assert str(datetime.now(timezone.utc)).split()[0] in exercises_statistic["dateTime"], (
                "Ошибка, дата в сервисе не зафиксирована")

        with aqas.step("Проверка информации о выстрелах, совершенных в завершенном упражнении"):
            assert exercises_statistic["numberOfShots"] == Hunter3D.NUMBER_SHOTS_ONE_HIT, (
                "Ошибка, выстрелы не зафиксированы в сервисе")

        with aqas.step("Проверка информации об очках в завершенном упражнении"):
            assert exercises_statistic["score"] == Hunter3D.SCORE_UI_ONE_HIT, (
                "Ошибка, очки не зафиксированы в сервисе")

    @pytest.mark.usefixtures("start_browser")
    @allure.title("combat_miss_hit_hit")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-719")
    def test_combat_miss_hit_hit(self, prepare_exercise_api):   # noqa: CFQ001
        """
            Проверка передачи данных о двух выстрелах из боеого оружия с широким размером экрана
            с промахом и 2мя попаданиями, предварительно выставив настройки тира через мутации API.
            Данные передаются по протоколу UDP из Jerboa в Unity-Hunter3d,
            после в Redis, далее в GQL в HunterAPI сервис и в WebUI с заполнением таблицы данными о выстрелах.
        """
        lane1_control_page = prepare_exercise_api

        with aqas.step("Сохранить HWID установленного оружия"):
            aqas.wait_until(
                method=lambda: isinstance(
                    ApiGatewayAdapter().query("laneDatas")[0]["shooters"][0]["weapons"][0]["hwid"], int),
                message="Нет значения hwid в ответе запроса laneDatas",
            )
            weapon_hwid = ApiGatewayAdapter().query("laneDatas")[0]["shooters"][0]["weapons"][0]["hwid"]

        with aqas.step("Формирования сообщение о выстреле, где есть промах"):
            miss_shot_message = utils.data_utils.encode_lightweight_combat_shot_message(
                weapon_hwid, Hunter3D.POINTX_MISS, Hunter3D.POINTY_MISS)

        with aqas.step("Получить сообщение от Redis о выстреле"):
            message_from_redis = get_shot_msg_from_redis("shot", miss_shot_message)

        with aqas.step("Получить данные из API для сравнения с данными в канале Redis"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")[0]["shooting"][0]

        with aqas.step("Проверка наличия данных о выстреле с промахом сообщения от Redis по ключу shot"):
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
            assert not message_from_redis["IsHitted"], (
                "В данных сообщения о выстреле c промахом зафиксирован неверный Результат")

        with aqas.step("Проверка передачи статистики из HunterAPI в WebUI и заполнения таблицы"):
            aqas.wait_until(
                method=lambda: int(
                    lane1_control_page.elements.NUMBER_OF_SHOTS_LBL.text) == Hunter3D.NUMBER_SHOTS_ONE_MISS,
                timeout=30,
                message="Ошибка, выстрелы не появились в UI",
            )
            assert int(lane1_control_page.elements.SCORE_LBL.text) == Hunter3D.SCORE_UI_ONE_MISS, (
                "Ошибка, очки не зафиксированы в UI")
            assert int(lane1_control_page.elements.NUMBER_OF_HITS_LBL.text) == Hunter3D.NUMBER_HITS_ONE_MISS, (
                "Ошибка, попадания не зафиксированы в UI")

        with aqas.step("Формирования сообщение о выстреле, где есть попадание"):
            hit_shot_message = utils.data_utils.encode_lightweight_combat_shot_message(
                weapon_hwid, Hunter3D.POINTX_HIT, Hunter3D.POINTY_HIT)

        with aqas.step("Получить сообщение от Redis о выстреле с попаданием"):
            message_from_redis = get_shot_msg_from_redis("shot", hit_shot_message)

        with aqas.step("Получить данные из API о 2ом выстреле для сравнения с данными в канале Redis"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")[0]["shooting"][1]

        with aqas.step("Проверка наличия данных о выстреле с попаданием в сообщении от Redis по ключу shot"):
            assert message_from_redis["LaneNumber"] == Hunter3D.FIRST_LANE, (
                "В данных сообщения о выстреле не зафиксирована полоса")
            assert message_from_redis["IsHitted"], (
                "В данных сообщения о выстреле не зафиксировано попадание")
            assert message_from_redis["Score"] == Hunter3D.SCORE_REDIS_ONE_HIT, (
                "В данных сообщения о выстреле не зафиксированы очки попадания")
            assert str(message_from_redis["PrefabName"]) == str(lane_datas["prefabName"]), (
                "В данных сообщения о выстреле Наименование префаба не совпадает со значением в API")
            assert int(message_from_redis["Score"]) == lane_datas["score"], (
                "В данных сообщения о выстреле Баллы  не совпадают со значением в API")
            assert message_from_redis["HitZoneName"] == lane_datas["hitZoneName"], (
                "В данных сообщения о выстреле Наименование зоны попадания не совпадает со значением в API")
            assert message_from_redis["TargetId"] == lane_datas["targetId"], (
                "В данных сообщения о выстреле Результат попадания не совпадает со значением в API")

        with aqas.step("Проверка передачи статистики из HunterAPI в WebUI и заполнения таблицы"):
            aqas.wait_until(
                method=lambda: int(
                    lane1_control_page.elements.NUMBER_OF_SHOTS_LBL.text) == Hunter3D.NUMBER_SHOTS_MISS_AND_HIT,
                timeout=30,
                message="Ошибка, выстрелы не появились в UI",
            )
            assert int(lane1_control_page.elements.SCORE_LBL.text) == Hunter3D.SCORE_UI_ONE_HIT, (
                "Ошибка, очки не зафиксированы в UI")
            assert int(lane1_control_page.elements.NUMBER_OF_HITS_LBL.text) == Hunter3D.NUMBER_HITS_ONE_HIT, (
                "Ошибка,  попадания не зафиксированы в UI")

        with aqas.step("Формирования сообщение о выстреле, где есть попадание"):
            hit_shot_message = utils.data_utils.encode_lightweight_combat_shot_message(
                weapon_hwid, Hunter3D.POINTX_HIT, Hunter3D.POINTY_HIT)

        with aqas.step("Получить сообщение от Redis о 3-ем выстреле-попадании"):
            message_from_redis = get_shot_msg_from_redis("shot", hit_shot_message)

        with aqas.step("Получить данные из API о 3ем выстреле для сравнения с данными в канале Redis"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")[0]["shooting"][2]

        with aqas.step("Проверка наличия данных о выстреле с попаданием в сообщении от Redis по ключу shot"):
            assert message_from_redis["LaneNumber"] == Hunter3D.FIRST_LANE, (
                "В данных сообщения о выстреле не зафиксирована полоса")
            assert message_from_redis["IsHitted"], (
                "В данных сообщения о выстреле не зафиксировано попадание")
            assert message_from_redis["Score"] == Hunter3D.SCORE_REDIS_ONE_HIT, (
                "В данных сообщения о выстреле не зафиксированы очки попадания")
            assert str(message_from_redis["PrefabName"]) == str(lane_datas["prefabName"]), (
                "В данных сообщения о выстреле Наименование префаба не совпадает со значением в API")
            assert int(message_from_redis["Score"]) == lane_datas["score"], (
                "В данных сообщения о выстреле Баллы  не совпадают со значением в API")
            assert message_from_redis["HitZoneName"] == lane_datas["hitZoneName"], (
                "В данных сообщения о выстреле Наименование зоны попадания не совпадает со значением в API")
            assert message_from_redis["TargetId"] == lane_datas["targetId"], (
                "В данных сообщения о выстреле Результат попадания не совпадает со значением в API")

        with aqas.step("Проверка передачи статистики из HunterAPI в WebUI и заполнения таблицы"):
            aqas.wait_until(
                method=lambda: int(lane1_control_page.elements.NUMBER_OF_SHOTS_LBL.text) == Hunter3D.NUMBER_SHOTS_3,
                timeout=30,
                message="Ошибка, выстрелы не появились в UI",
            )
            assert int(lane1_control_page.elements.SCORE_LBL.text) == Hunter3D.SCORE_UI_TWO_HIT, (
                "Ошибка, очки не зафиксированы в UI")
            assert int(lane1_control_page.elements.NUMBER_OF_HITS_LBL.text) == Hunter3D.NUMBER_HITS_TWO, (
                "Ошибка,  попадания не зафиксированы в UI")

        with aqas.step("Остановить упражнение"):
            if not is_located(lane1_control_page.elements.STOP_DISABLED_LBL):
                lane1_control_page.elements.STOP_BTN.click()

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert = AlertForm()
            if is_located(alert.elements.NOTIFICATIONS_FORM):
                alert.wait_for_notifications_invisible()

        with aqas.step("Проверка совпадения заданного статуса полосы  с UI со значением с backend"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["sessionState"] == StateEnum.STOP.value,
                message="Ошибка, упражнение не остановилось",
            )

        with aqas.step("Сделать GraphQL запрос exercisesStatistic"):
            exercises_statistic = ApiGatewayAdapter().query("exercisesStatistic")[-1]

        with aqas.step("Проверка наличия ответа"):
            assert exercises_statistic["exerciseType"], "Нет ответа от запроса"

        with aqas.step("Проверка информации об имени завершенного упражнения"):
            assert exercises_statistic["exerciseName"] == Hunter3D.EX_NAME_JERBOA, (
                "Ошибка, имя упр. в сервисе не зафиксировано")

        with aqas.step("Проверка информации о дате в завершенном упражнении"):
            assert str(datetime.now(timezone.utc)).split()[0] in exercises_statistic["dateTime"], (
                "Ошибка, дата в сервисе не зафиксирована")

        with aqas.step("Проверка информации о выстрелах, совершенных в завершенном упражнении"):
            assert exercises_statistic["numberOfShots"] == Hunter3D.NUMBER_SHOTS_3, (
                "Ошибка, выстрелы не зафиксированы в сервисе")

        with aqas.step("Проверка информации об очках в завершенном упражнении"):
            assert exercises_statistic["score"] == Hunter3D.SCORE_UI_TWO_HIT, (
                "Ошибка, очки не зафиксированы в сервисе")
