class Car:
    def __init__(self, year, make):
        self.__year_model = year
        self.__make = make
        self.__speed = 0

    def accelerate(self):
        """
        Метод ускорения

        :return:
        """
        self.__speed += 5

    def brake(self):
        self.__speed -= 5

    @property
    def get_speed(self):
        return self.__speed
