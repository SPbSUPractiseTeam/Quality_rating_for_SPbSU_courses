from django.db import models
from django.contrib.auth.models import User
from enum import Enum


class TestTypeChoice(Enum):
    CHK = "Проверочный тест"
    CTRL = "Котнрольный тест"


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    russian_title = models.CharField(max_length=100)


class Log(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    load_date = models.DateTimeField()

    def __str__(self):
        if self.load_date:
            return self.load_date.strftime('%d.%m.%Y')
        else:
            return "No data"


class Module(models.Model):
    TO_TEN_WORDS = ['Первый', 'Второй', 'Третий', 'Четвертый', 'Пятый', 'Шестой', 'Седьмой', 'Восьмой',
                    'Девятый', 'Десятый']
    FROM_TEN_TO_TWENTY_PREFIXES = ['Один', 'Две', 'Три', 'Четыр', 'Пят', 'Шест', 'Сем', 'Восем', 'Девят']
    FROM_TEN_TO_TWENTY_SUFFIX = 'надцатый'
    TEN_WORDS = ['Двадцать', 'Тридцать', 'Сорок', 'Пятьдесят', 'Шестьдесят', 'Семьдесят', 'Восемьдесят',
                 'Девяносто']
    log = models.ForeignKey(Log, on_delete=models.CASCADE)
    number = models.IntegerField()
    hash_str_id = models.CharField(max_length=50)

    def __str__(self):
        if self.number <= 10:
            module_name = Module.TO_TEN_WORDS[self.number - 1]
        elif self.number < 20:
            module_name = Module.FROM_TEN_TO_TWENTY_PREFIXES[self.number - 11] + Module.FROM_TEN_TO_TWENTY_SUFFIX
        else:
            module_name = Module.TEN_WORDS[self.number // 10 - 2]
            if self.number % 10 != 0:
                module_name += (' ' + Module.TO_TEN_WORDS[self.number % 10 - 1])
        return module_name + ' модуль'


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    number = models.IntegerField()
    hash_str_id = models.CharField(max_length=50)
    link = models.CharField(max_length=300)


class Video(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    chart_link = models.CharField(max_length=300)
    number = models.IntegerField()
    material_viewed = models.FloatField()
    users_watched = models.FloatField()
    is_most_viewed = models.BooleanField()

    def get_material_viewed(self):
        return "%.2f" % (self.material_viewed * 100)

    def get_users_watched(self):
        return "%.2f" % (self.users_watched * 100)


class Test(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=[(type.name, type.value) for type in TestTypeChoice])
    hash_str_id = models.CharField(max_length=100)
    number = models.IntegerField()


class Attempt(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    number = models.IntegerField()
    average_grade = models.FloatField()
    median = models.FloatField()
    max_grade = models.FloatField()
    number_of_solutions = models.IntegerField()
    questions = models.TextField()

    def get_questions(self):
        return self.questions.split(',')

    def get_question_list(self):
        questions_list = self.get_questions()
        questions_list = ['Вопрос {}. {}%'.format(index, '%.3f' % float(percent)) for question in questions_list for
                          index, percent in [question.split(')')]]
        return questions_list

    def get_average_grade(self):
        return "%.2f" % self.average_grade

    def get_median(self):
        return "%.2f" % self.median

    def get_max_grade(self):
        return "%.2f" % self.max_grade
