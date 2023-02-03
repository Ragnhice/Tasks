import allure
import aqas
import pytest
from faker import Faker

from models.api.api_gateway_adapter import ApiGatewayAdapter
from models.db.user import User
from utils.constants import API
from utils.data_utils import compare_dicts
from utils.enums import Gender, UserTypeEnum


@allure.parent_suite("api")
@allure.suite("HunterApi")
@allure.sub_suite("crud")
class TestsCrudUser:
    ANONYM_USER_ID = ""

    @pytest.mark.dependency()
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-379")
    @allure.title("create_user")
    def test_create_user(self):
        user_data_to_create = {
            "createUser": {
                "userInput": {
                    "firstName": Faker().first_name(),
                    "middleName": Faker().first_name(),
                    "lastName": Faker().last_name(),
                    "height": Faker().pyfloat(),
                    "birthCity": Faker().city(),
                    "birthDate": Faker().date(),
                    "appointment": Faker().domain_word(),
                    "personalId": Faker().isbn10(),
                    "title": Faker().isbn10(),
                    "archived": True,
                    "memo": Faker().isbn10(),
                    "role": UserTypeEnum.SHOOTER,
                    "gender": Gender.MALE,
                    "login": Faker().first_name(),
                    "password": API.TEST_PASSWORD_1,
                    "dutyDate": Faker().random_int(),
                    "unitId": 1,
                },
            },
        }
        user_data_expected = user_data_to_create["createUser"]["userInput"]
        with aqas.step("Отправка запроса"):
            user_data_actual = ApiGatewayAdapter().mutation("createUser", user_data_to_create)

        with aqas.step("Проверка типа возвращаемых аргументов"):
            assert all(isinstance(user_data_actual[key], str) for key in [
                "shortName", "memo", "title", "personalId", "appointment", "birthCity"]), "Не все поля типа str"
            assert isinstance(user_data_actual["height"], float), "Ошибка, тип не равен float"
            assert isinstance(user_data_actual["dutyDate"], int), "Ошибка, тип не равен int"
            assert user_data_actual["archived"], "Ошибка,нет архивации"

        with aqas.step("Проверить в ответе запроса, что мутация обновила аргументы поля пользователя"):
            comp_keys = ["firstName", "middleName", "lastName", "height", "birthCity",
                         "appointment", "personalId", "dutyDate", "title", "memo", "login"]
            compare_dicts(user_data_expected, user_data_actual, comp_keys)

        with aqas.step("Записать аргументы поля пользователя для сравнения с полем таблицы"):
            TestsCrudUser.USER_ID = user_data_actual["id"]

    @allure.title("Наличие записи с новым пользователем из таблицы users в бд vega")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-730")
    @pytest.mark.dependency(depends=["test_create_user"], scope="class")
    def test_fetch_db_create_user(self):
        with aqas.step("Отправка запроса"):
            users = ApiGatewayAdapter().query("users")
        with aqas.step("Проверка наличия ответа"):
            assert users[0]["id"], "Нет ответа от запроса"
        with aqas.step("Проверка типа"):
            assert isinstance(users[0]["id"], int), "Ошибка тип не равен int"
        with aqas.step("Проверка типа"):
            assert isinstance(users[0]["shortName"], str), "Ошибка тип не равен str"

        with aqas.step("Парсинг словаря с пользователями для создания словаря с 1 пользователем"):
            user = [item for item in users if item["id"] == TestsCrudUser.USER_ID][0]

        with aqas.step("Проверка наличия записи с новым пользователем в таблице vega.users"):
            db_data = User.get_by_id(TestsCrudUser.USER_ID)
            assert db_data, "Нет данных с новым пользователем в таблице"
            assert db_data.first_name == user["firstName"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.middle_name == user["middleName"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.last_name == user["lastName"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.height == user["height"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.birth_city == user["birthCity"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.appointment == user["appointment"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.duty_date == user["dutyDate"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.personal_id == user["personalId"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.title == user["title"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.archived == user["archived"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.memo == user["memo"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.login == user["login"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.password == user["password"], "Значение в таблице и в ответе запроса не совпадают"

    @pytest.mark.dependency(depends=["test_create_user"], scope="class")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-380")
    @allure.title("update_user")
    def test_update_user(self):
        user_data_to_update = {
            "updateUser": {
                "userInput": {
                    "id": TestsCrudUser.USER_ID,
                    "firstName": Faker().first_name(),
                    "middleName": Faker().first_name(),
                    "lastName": Faker().last_name(),
                    "height": Faker().pyfloat(),
                    "birthCity": Faker().city(),
                    "birthDate": Faker().date(),
                    "appointment": Faker().domain_word(),
                    "personalId": Faker().isbn10(),
                    "title": Faker().isbn10(),
                    "archived": True,
                    "memo": Faker().isbn10(),
                    "role": UserTypeEnum.SHOOTER,
                    "gender": Gender.MALE,
                    "dutyDate": Faker().random_int(),
                    "login": Faker().first_name(),
                    "password": API.TEST_PASSWORD_2,
                },
            },
        }
        user_data_expected = user_data_to_update["updateUser"]["userInput"]
        user_data_actual = ApiGatewayAdapter().mutation("updateUser", user_data_to_update)
        with aqas.step("Проверить в ответе запроса, что мутация обновила аргументы  поля пользователя"):
            comp_keys = ["firstName", "middleName", "lastName", "height", "birthCity",
                         "appointment", "personalId", "dutyDate", "title", "memo", "login"]
            compare_dicts(user_data_expected, user_data_actual, comp_keys)

    @allure.title("Обновление аргументов поля пользователя из таблицы users в бд vega")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-731")
    @pytest.mark.dependency(depends=["test_update_user"], scope="class")
    def test_fetch_db_update_user(self):
        with aqas.step("Отправка запроса"):
            users = ApiGatewayAdapter().query("users")
        with aqas.step("Проверка наличия ответа и типа поля в ответе"):
            assert isinstance(users[0]["id"], int), "Ошибка тип не равен int"
        with aqas.step("Проверка типа"):
            assert isinstance(users[0]["shortName"], str), "Ошибка тип не равен str"

        with aqas.step("Парсинг словаря с пользователями для создания словаря с 1 пользователем"):
            user = [item for item in users if item["id"] == TestsCrudUser.USER_ID][0]

        with aqas.step("Проверка обновления записи в таблице vega.users"):
            db_data = User.get_by_id(TestsCrudUser.USER_ID)
            assert db_data, "Нет данных с новым пользователем в таблице"
            assert db_data.id == user["id"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.first_name == user["firstName"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.middle_name == user["middleName"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.last_name == user["lastName"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.height == user["height"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.birth_city == user["birthCity"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.appointment == user["appointment"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.duty_date == user["dutyDate"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.personal_id == user["personalId"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.title == user["title"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.archived == user["archived"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.memo == user["memo"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.login == user["login"], "Значение в таблице и в ответе запроса не совпадают"
            assert db_data.password == user["password"], "Значение в таблице и в ответе запроса не совпадают"

    @pytest.mark.dependency()
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-419")
    @allure.title("create_anonymous_user")
    def test_create_anonymous_user(self):
        with aqas.step("Отправка запроса с мутацией"):
            user = ApiGatewayAdapter().mutation("addAnonymousUser")
        with aqas.step("Сохраняем полученные данные в переменные"):
            TestsCrudUser.ANONYM_USER_ID = user["id"]
        with aqas.step("Проверка типа"):
            assert isinstance(user["id"], int)
        with aqas.step("Проверка типа"):
            assert isinstance(user["height"], float)
        with aqas.step("Проверка типа"):
            assert isinstance(user["archived"], bool)
        with aqas.step("Проверка типа"):
            assert isinstance(user["shortName"], str)
        with aqas.step("Проверка типа"):
            assert isinstance(user["lastName"], str)
        with aqas.step("Проверка приcвоенного аргумента"):
            assert str(user["role"]) == API.ROLE[0], "Назначенная роль не стрелок"

    @pytest.mark.dependency(depends=["test_create_user"], scope="class")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-381")
    @allure.title("delete_user")
    def test_delete_user(self):
        result = ApiGatewayAdapter().remove_users_by_id([TestsCrudUser.USER_ID])
        with aqas.step("Проверка наличия ответа"):
            assert result == 1, "Пользователи не удалены"

    @allure.title("Обновление аргументов поля пользователя из таблицы users в бд vega")
    @pytest.mark.test_case("https://jira.steor.tech/browse/VEGA2-732")
    @pytest.mark.dependency(depends=["test_delete_user"], scope="class")
    def test_fetch_db_remove_user(self):
        with aqas.step("Удаление поля пользователя из таблицы users в бд vega"):
            db_data = User.get_by_id(TestsCrudUser.USER_ID)
            with aqas.step("Проверяем отсутствие значений"):
                assert db_data is None, "Пользователь не удален из бд, запись осталась"
