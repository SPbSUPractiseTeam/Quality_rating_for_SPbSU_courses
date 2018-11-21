from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    russian_title = models.CharField(max_length=100)


class LoadDate(models.Model):
    date = models.DateTimeField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        if self.date:
            return self.date.strftime('%d.%m.%Y')
        else:
            return "No data"


class Week(models.Model):
    WEEK_ORDINAL_NAMES = ['Первая', 'Вторая', 'Третья', 'Четвертая', 'Пятая', 'Шестая', 'Седьмая', 'Восьмая', 'Девятая',
                          'Десятая', 'Одиннадцатая']
    date = models.ForeignKey(LoadDate, on_delete=models.CASCADE)
    number = models.IntegerField()
    hash_str_id = models.CharField(max_length=50)

    def __str__(self):
        return Week.WEEK_ORDINAL_NAMES[self.number - 1] + ' неделя'


class Video(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    chart_link = models.CharField(max_length=300)
    link = models.CharField(max_length=300)
    number = models.IntegerField()
    material_viewed = models.FloatField()
    users_watched = models.FloatField()
    hash_str_id = models.CharField(max_length=50)
    is_most_viewed = models.BooleanField()

    def get_material_viewed(self):
        return "%.2f" % (self.material_viewed * 100)

    def get_users_watched(self):
        return "%.2f" % (self.users_watched * 100)


class Test(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    link = models.CharField(max_length=300)
    hash_str_id = models.CharField(max_length=100)
    number = models.IntegerField()


class Attempt(models.Model):
    number = models.IntegerField()
    average_grade = models.FloatField()
    median = models.FloatField()
    max_grade = models.FloatField()
    number_of_solutions = models.IntegerField()
    questions = models.TextField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    def get_questions(self):
        return self.questions.split(',')

    def get_question_gen(self):
        questions_list = self.get_questions()
        indexes = [int(i + 1) for i in range(len(questions_list))]
        return ('Вопрос {}. {}%'.format(index, '%.3f' % float(question)) for index, question in
                zip(indexes, questions_list))

    def get_average_grade(self):
        return "%.2f" % self.average_grade

    def get_median(self):
        return "%.2f" % self.median

    def get_max_grade(self):
        return "%.2f" % self.max_grade
