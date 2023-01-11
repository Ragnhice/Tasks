class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @property
    def get_name(self):
        """
        Метод возвращающий имя

        :return:
        """
        return self.name

    #@property
    def get_age(self):
        #"""
        #Метод возвращающий возраст
#
        #:return:
        #"""
        return self.age
