# pylint: disable=too-many-statements

import allure
import aqas
import pytest

from models.api.api_gateway_adapter import ApiGatewayAdapter
from models.ui.forms.conditions_menu_form import ConditionsMenuForm
from models.ui.forms.confirm_form import ConfirmForm
from models.ui.forms.exercise_menu_form import ExerciseMenuForm
from models.ui.forms.shooters_chose_form import ShootersChoseForm
from models.ui.forms.shooting_settings_form import ShootingSettingsForm
from models.ui.forms.side_bar_form import SideBarForm
from models.ui.forms.alert_form import AlertForm
from steps.auth_steps import get_auth_admin
from utils.constants import UI
from utils.element_utils import is_located
from utils.enums import ScreenSizeEnum, SeasonEnum, ShooterPositionEnum, StateEnum, WeaponModeEnum


@allure.parent_suite("ui")
@allure.suite("Main scenario")
@pytest.mark.usefixtures("start_browser")
class TestScenario:
    """
    Класс, который содержит действия тестов:
    - при проверке выбора и установки настроек тира (шаг 1);
    - при проверке выбора и установки упражнения (шаг 2);
    - при проверке выбора и установки условий на полосе (шаг 3);
    - при проверке выбора и установки стрелка на полосе (шаг 4);
    - при проверке запуска и остановки упражнения (шаг 5).
    """

    @allure.title("main_scenario_1_step")
    @pytest.mark.test_case("https://jira.---")
    def test_scenario_1_step(self):
        """Выбор и установка настроек тира."""
        with aqas.step("Аутентификация администратором и переход на страницу управления полосами"):
            lanes_control_page = get_auth_admin()

        with aqas.step("Открыть боковое меню"):
            lanes_control_page.elements.MENU_BTN.click()
            sidebar_page = SideBarForm()
            sidebar_page.elements.LOADER.state.wait_for_invisible()
            assert sidebar_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.step("Открыть окно установки режима работы тира"):
            sidebar_page.elements.SETTINGS_BTN.click()
            sidebar_page.elements.SHOOTING_MODE_BTN.click()
            shooting_settings_page = ShootingSettingsForm()
            sidebar_page.elements.LOADER.state.wait_for_invisible()
            assert shooting_settings_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.step("Сменить режим работы тира на широкий экран c 2мя полосами с охолощенным оружием"):
            shooting_settings_page.elements.WIDE_BTN.click()
            shooting_settings_page.elements.AMOUNT_LANE_BTN.click()
            shooting_settings_page.elements.TWO_LANES_LBL.click()
            shooting_settings_page.elements.EMASCULATED_WEAPON.click()
            shooting_settings_page.elements.APPLY_BTN.wait_and_click()
            confirm_form = ConfirmForm()
            assert confirm_form.is_wait_for_form_load(), "Страница не загрузилась"
            confirm_form.elements.CONFIRM_BTN.click()
            confirm_form.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Проверить с UI, что появилось уведомление о смене режима работы тира"):
            alert = AlertForm()
            assert alert.is_wait_for_form_load(), "Уведомление не появилось"
            aqas.wait_until(
                method=lambda: UI.ATTENTOION in alert.text_summary() or UI.SETTINGS_UPDATED in alert.text_summary(),
                message="Нет уведомления об установке новых настроек тира",
            )

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert.wait_for_notifications_invisible()

        with aqas.step("Отправка запроса shootingMode на backend"):
            shooting_mode = ApiGatewayAdapter().query("shootingMode")
        with aqas.step("Проверка установленных значений"):
            assert shooting_mode["laneCount"] == 2, "Ошибка установки количества полос"
            assert shooting_mode["screenSize"] == ScreenSizeEnum.WIDE.value, "Ошибка установки ширины экрана"
            assert shooting_mode["weaponMode"] == WeaponModeEnum.LIGHTWEIGHT.value, "Ошибка установки режима оружия"

        with aqas.step("Проверить, что полоса свободна"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")
            assert lane_datas[0]["laneNumber"] == 1, "Ошибка номера полосы"
            assert lane_datas[0]["isBusy"] is False, "Ошибка, 1 полоса занята после устаовки новых настроек тира"

    @allure.title("main_scenario_2_step")
    @pytest.mark.test_case("https://jira.---")
    def test_scenario_2_step(self, go_lane1):
        """Выбор и установка упражнения."""

        lane1_control_page = go_lane1

        with aqas.step("Занять полосу, если она освобождена"):
            if is_located(lane1_control_page.elements.LANE_IS_FREE_LBL):
                lane1_control_page.elements.BUSY_LANE_BTN.click()
                lane1_control_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Проверить, что полоса стала занятой"):
            assert is_located(lane1_control_page.elements.LANE_IS_BUSY_LBL), "Полоса не стала занятой"

        with aqas.step("Переход на страницу установки упражнения"):
            lane1_control_page.elements.EX_MENU_BTN.click()
            ex_menu_page = ExerciseMenuForm()
            ex_menu_page.elements.LOADER.state.wait_for_invisible()
            assert ex_menu_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.step("Выбрать упражнение из списка"):
            ex_menu_page.choose_ex_in_list(2)

        with aqas.step("Сохранить данные c именем 2-го упражнения"):
            ex_id_from_ui = ex_menu_page.get_name_chosen_ex(2).split(" ")[-1][:-1]

        with aqas.step("Сохранить выбор"):
            ex_menu_page.elements.SAVE_EX_BTN.click()
            ex_menu_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Проверить с UI, что упражнение установилось"):
            alert = AlertForm()
            assert alert.is_wait_for_form_load(), "Уведомление не появилось"
            aqas.wait_until(
                method=lambda: (UI.SUM_NOTIFIC_EX_SETTING in alert.text_summary()),
                message="Нет уведомления об установке упражнения",
            )

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert.wait_for_notifications_invisible()

        with aqas.step("Отправка запроса laneDatas на backend"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")
            with aqas.step("Проверка наличия ответа"):
                assert lane_datas[0]["laneNumber"], "Нет ответа от запроса"
            with aqas.step("Проверка совпадения заданных значений с UI и значений с backend"):
                assert lane_datas[0]["exerciseId"] == int(ex_id_from_ui), "Ошибка, упражнение не установилось"

        with aqas.step("Вернуться на страницу управления 1 полосой"):
            ex_menu_page.elements.BACK_BTN.click()
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            assert lane1_control_page.is_wait_for_form_load(), "Страница не загрузилась"

    @allure.title("main_scenario_3_step")
    @pytest.mark.test_case("https://jira.---")
    def test_scenario_3_step(self, go_lane1):
        """Выбор и установка условий на полосе."""

        season_set_from_ui = SeasonEnum.SUMMER.value
        time_from_ui = 21

        lane1_control_page = go_lane1
        with aqas.step("Переход на страницу установки условий"):
            lane1_control_page.elements.CONDITIONS_MENU_BTN.click()
            сonditions_menu_page = ConditionsMenuForm()
            сonditions_menu_page.elements.LOADER.state.wait_for_invisible()
            assert сonditions_menu_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.step("Сменить сезон на весну"):
            сonditions_menu_page.elements.SEASON_TO_CHOSE_BTN.click()
            сonditions_menu_page.elements.SPRING_SEASON_BTN.click()

        with aqas.step("Проверка соответствия только что выбранного сезона с UI"):
            aqas.wait_until(
                method=lambda: сonditions_menu_page.elements.SEASON_CHOSEN_LBL.text == UI.SPRING,
                message="Сезон не установился",
            )

        with aqas.step("Сменить сезон на лето"):
            сonditions_menu_page.elements.SEASON_TO_CHOSE_BTN.click()
            сonditions_menu_page.elements.SUMMER_SEASON_BTN.click()

        with aqas.step("Проверка соответствия только что выбранного сезона с UI"):
            aqas.wait_until(
                method=lambda: сonditions_menu_page.elements.SEASON_CHOSEN_LBL.text == UI.SUMMER,
                message="Сезон не установился",
            )

        with aqas.step("Сменить время суток на ночь"):
            сonditions_menu_page.elements.DAY_TYPE_OPEN_LIST_BTN.click()
            сonditions_menu_page.elements.NIGHT_BTN.wait_and_click()

        with aqas.step("Проверка соответствия только что выбранного времени суток с UI"):
            aqas.wait_until(
                method=lambda: сonditions_menu_page.elements.TIME_OF_DAY_CHOSEN_LBL.text == UI.NIGHT,
                message="Время суток не установилось",
            )

        with aqas.step("Сменить время суток на вечер"):
            сonditions_menu_page.elements.DAY_TYPE_OPEN_LIST_BTN.wait_and_click()
            сonditions_menu_page.elements.EVENING_BTN.wait_and_click()

        with aqas.step("Проверка соответствия только что выбранного времени суток с UI"):
            aqas.wait_until(
                method=lambda: сonditions_menu_page.elements.TIME_OF_DAY_CHOSEN_LBL.text == UI.EVENING,
                message="Время суток не установилось",
            )

        with aqas.step("Сменить точное время"):
            сonditions_menu_page.elements.TIME_OPEN_LIST_BTN.click()
            сonditions_menu_page.elements.TIME_IN_LIST_21_BTN.click()

        with aqas.step("Сменить позицию"):
            сonditions_menu_page.elements.LYING_POSITION_BTN.click()

        with aqas.step("Проверка соответствия только что выбранной позиции с UI"):
            assert is_located(сonditions_menu_page.elements.LYING_IS_CHOSEN_LBL), "Позиция лежа не установилась в ui"

        with aqas.step("Сменить позицию"):
            сonditions_menu_page.elements.SITTING_POSITION_BTN.click()
            position_from_ui = ShooterPositionEnum.KNEES.value

        with aqas.step("Сохранить"):
            сonditions_menu_page.elements.SAVE_CONDITION_BTN.click()
            сonditions_menu_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Проверить, что условия обновились"):
            alert = AlertForm()
            assert alert.is_wait_for_form_load(), "Уведомление не появилось"
            aqas.wait_until(
                method=lambda: alert.text_summary() == UI.CONDITION_UPDATED,
                message="Условия не обновились",
            )

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert.wait_for_notifications_invisible()

        with aqas.step("Отправка запроса laneDatas на backend"):
            lane_datas = ApiGatewayAdapter().query("laneDatas")
        with aqas.step("Проверка наличия ответа"):
            assert lane_datas[0]["laneNumber"], "Нет ответа от запроса"
        with aqas.step("Проверка совпадения заданных значений с UI и значений с backend"):
            assert lane_datas[0]["environment"]["season"] == season_set_from_ui, "Ошибка, сезон не установился"
            assert lane_datas[0]["environment"]["shooterPosition"] == position_from_ui, "Ошибка установки позиции"
            assert lane_datas[0]["environment"]["hour"] == time_from_ui, "Ошибка установки точного времени"

        with aqas.step("Вернуться на страницу управления 1 полосой"):
            сonditions_menu_page.elements.BACK_BTN.click()
            сonditions_menu_page.elements.LOADER.state.wait_for_invisible()
            assert lane1_control_page.is_wait_for_form_load(), "Страница не загрузилась"

    @allure.title("main_scenario_4_step")
    @pytest.mark.test_case("https://jira.---)
    def test_scenario_4_step(self, go_lane1):
        """Выбор и установка стрелка на полосе ."""

        lane1_control_page = go_lane1

        with aqas.step("Переход на страницу выбора стрелков на полосу"):
            lane1_control_page.elements.SHOOTERS_MENU_BTN.click()
            shooter_chose_page = ShootersChoseForm()
            shooter_chose_page.elements.LOADER.state.wait_for_invisible()
            assert shooter_chose_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.step("Удалить стрелка"):
            if is_located(shooter_chose_page.elements.DELETE_SHOOTER_BTN):
                shooter_chose_page.elements.DELETE_SHOOTER_BTN.click()

        with aqas.step("Добавить стрелка"):
            shooter_chose_page.elements.ADD_SHOOTER_BTN.wait_and_click()
            shooter_chose_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Выбрать стрелка"):
            shooter_chose_page.elements.SHOOTER_TO_CHOSE_LIST_DRDW.click()
            shooter_chose_page.elements.LOADER.state.wait_for_invisible()
            shooter_chose_page.elements.SHOOTER_IN_LIST_1_BTN.wait_and_click()

        with aqas.step("Проверка автозаполнения поля выбора оружия и боеприпаса"):
            shooter_chose_page.elements.CHOSEN_WEAPON_DRDW.reset()
            shooter_chose_page.elements.CHOSEN_AMMO_DRDW.reset()
            aqas.wait_until(
                method=lambda: shooter_chose_page.elements.CHOSEN_WEAPON_DRDW.wait_text() != UI.EMPTY,
                message="Поле выбора оружия",
            )
            aqas.wait_until(
                method=lambda: shooter_chose_page.elements.CHOSEN_AMMO_DRDW.wait_text() != UI.EMPTY,
                message="Поле выбора боеприпаса пустое",
            )

        with aqas.step("Добавить стрелку оружие"):
            shooter_chose_page.elements.ADD_WEAPON_BTN.reset()
            shooter_chose_page.elements.ADD_WEAPON_BTN.click()
            shooter_chose_page.elements.LOADER.state.wait_for_invisible()

        with aqas.pre_step("Вернуться на страницу управления 1 полосой"):
            shooter_chose_page.elements.BACK_BTN.reset()
            shooter_chose_page.elements.BACK_BTN.click()
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            assert lane1_control_page.is_wait_for_form_load(), "Страница не загрузилась"

    @allure.title("main_scenario_5_step")
    @pytest.mark.test_case("https://jira.---")
    def test_scenario_5_step(self, go_lane1):  # noqa: CFQ001
        """Проверка запуска и остановки упражнения."""

        lane1_control_page = go_lane1

        with aqas.step("Запуск упражнения"):
            lane1_control_page.elements.PLAY_BTN.click()
            lane1_control_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Подтвердить выбор оружия"):
            alert = AlertForm()
            if is_located(lane1_control_page.elements.CHOSEN_WEAPON_DRDN):
                with aqas.step("Проверка автозаполнения поля выбора оружия и поля выбора  боеприпаса"):
                    aqas.wait_until(
                        method=lambda: lane1_control_page.elements.CHOSEN_WEAPON_DRDN.wait_text() != UI.EMPTY,
                        message="Поле выбора оружия",
                    )
                    aqas.wait_until(
                        method=lambda: lane1_control_page.elements.CHOSEN_AMMO_DRDN.wait_text() != UI.EMPTY,
                        message="Поле выбора боеприпаса пустое",
                    )
                lane1_control_page.elements.CONFIRM_CHOSEN_WEAPON_BTN.click()
                lane1_control_page.elements.LOADER.state.wait_for_invisible()
                with aqas.step("Проверить c UI, что стрелок установлен"):
                    assert alert.is_wait_for_form_load(), "Уведомление не появилось"
                    aqas.wait_until(
                        method=lambda: (UI.SHOOTER_SETTED in alert.text_detail() or UI.SUM_NOTIFIC_SHOOTERS_SETTING
                                        in alert.text_summary() or UI.WEAPON_PARK_AVAI_UP
                                        in alert.text_summary() or UI.EX_IS_STARTED
                                        in alert.text_summary() or UI.EX_IS_STARTED in alert.text_detail()),
                        message="Нет уведомления об установке стрелка",
                    )
                    alert.close()

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert.wait_for_notifications_invisible()

        with aqas.step("Проверка совпадения заданного статуса полосы  с UI со значением с backend"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["sessionState"] == StateEnum.START.value,
                message="Ошибка, упражнение не в ожидаемом статусе",
            )

        with aqas.step("Приостановить упражнение, если оно запущено"):
            if not is_located(lane1_control_page.elements.PAUSE_DISABLED_LBL):
                lane1_control_page.elements.PAUSE_BTN.click()
                lane1_control_page.elements.LOADER.state.wait_for_invisible()
                with aqas.step("Проверить c UI, что упражнение поставлено на паузу"):
                    aqas.wait_until(
                        method=lambda: alert.text_detail() == UI.EX_IS_PAUSED,
                        message="Нет уведомления об установке упражнения на паузу",
                    )
                with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
                    alert.wait_for_notifications_invisible()

        with aqas.step("Проверка совпадения заданного статуса полосы  с UI со значением с backend"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["sessionState"] == StateEnum.PAUSE.value,
                message="Ошибка, упражнение не приостановилось",
            )

        with aqas.step("Остановить упражнение, если оно запущено"):
            if not is_located(lane1_control_page.elements.STOP_DISABLED_LBL):
                lane1_control_page.elements.STOP_BTN.click()

        with aqas.step("Проверить c UI, что упражнение остановилось"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: alert.text_detail() == UI.EX_IS_STOPPED,
                message="Нет уведомление об остановке",
            )

        with aqas.step("Подождать исчезновения уведомления и загрузки страницы"):
            alert.wait_for_notifications_invisible()

        with aqas.step("Остановить упражнение, если оно запущено"):
            lane1_control_page.elements.STOP_DISABLED_LBL.reset()
            lane1_control_page.elements.STOP_BTN.reset()
            if not is_located(lane1_control_page.elements.STOP_DISABLED_LBL):
                lane1_control_page.elements.STOP_BTN.click()
                lane1_control_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Проверка совпадения заданного статуса полосы  с UI со значением с backend"):
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["sessionState"] == StateEnum.STOP.value,
                message="Ошибка, упражнение не остановилось",
            )

        with aqas.step("Переход на страницу выбора стрелков на полосу"):
            lane1_control_page.elements.SHOOTERS_MENU_BTN.click()
            shooter_chose_page = ShootersChoseForm()
            shooter_chose_page.elements.LOADER.state.wait_for_invisible()
            assert shooter_chose_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.step("Удалить стрелка"):
            shooter_chose_page.elements.DELETE_SHOOTER_BTN.reset()
            if is_located(shooter_chose_page.elements.DELETE_SHOOTER_BTN):
                shooter_chose_page.elements.DELETE_SHOOTER_BTN.click()

        with aqas.step("Добавить стрелка"):
            shooter_chose_page.elements.ADD_SHOOTER_BTN.reset()
            shooter_chose_page.elements.ADD_SHOOTER_BTN.wait_and_click()
            shooter_chose_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Выбрать стрелка"):
            shooter_chose_page.elements.SHOOTER_TO_CHOSE_LIST_DRDW.reset()
            shooter_chose_page.elements.SHOOTER_TO_CHOSE_LIST_DRDW.click()
            shooter_chose_page.elements.SHOOTER_IN_LIST_1_BTN.reset()
            shooter_chose_page.elements.SHOOTER_IN_LIST_1_BTN.click()

        with aqas.pre_step("Проверка автозаполнения поля выбора оружия и боеприпаса"):
            aqas.wait_until(
                method=lambda: shooter_chose_page.elements.CHOSEN_WEAPON_DRDW.wait_text() != UI.EMPTY,
                message="Поле выбора оружия",
            )

        with aqas.pre_step("Проверка автозаполнения поля выбора боеприпаса"):
            aqas.wait_until(
                method=lambda: shooter_chose_page.elements.CHOSEN_AMMO_DRDW.wait_text() != UI.EMPTY,
                message="Поле выбора боеприпаса пустое",
            )

        with aqas.pre_step("Добавить оружие стрелку"):
            shooter_chose_page.elements.ADD_WEAPON_BTN.click()
            shooter_chose_page.elements.LOADER.state.wait_for_invisible()
            assert shooter_chose_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.pre_step("Вернуться на страницу управления 1 полосой"):
            shooter_chose_page.elements.BACK_BTN.reset()
            shooter_chose_page.elements.BACK_BTN.click()
            lane1_control_page.elements.LOADER.state.wait_for_invisible()
            assert lane1_control_page.is_wait_for_form_load(), "Страница не загрузилась"

        with aqas.step("Освободить полосу, если она занята"):
            if is_located(lane1_control_page.elements.LANE_IS_BUSY_LBL) or is_located(
                    lane1_control_page.elements.LANE_IS_UNAVAILABLE_LBL):
                lane1_control_page.elements.BUSY_LANE_BTN.reset()
                lane1_control_page.elements.BUSY_LANE_BTN.click()
                lane1_control_page.elements.LOADER.state.wait_for_invisible()

        with aqas.step("Проверка совпадения занятости полосы с UI со значением с backend"):
            aqas.wait_until(
                method=lambda: ApiGatewayAdapter().query("laneDatas")[0]["isBusy"] is False,
                message="Ошибка, полоса не освободилась",
            )
