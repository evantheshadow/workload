from django.db import models
from django.contrib.auth.models import User

# Create your models here.

SUBJECT_TYPE_CHOICES = ( # «Справочник» для выбора вида занятия
    ('Теория', 'Теоритическая часть'),
    ('Практика', 'Практическая часть'),
)


class AcademDegree(models.Model): # Таблица «Ученая степень». Показывает, какую ученую степень имеет преподаватель.
    name = models.CharField(
        max_length=100, 
        verbose_name='Название ученой степени'
    )

    class Meta:
        verbose_name = 'Ученая степень'
        verbose_name_plural = 'Ученые степени'

    def __str__(self): # Для отображения имени объектов в админ-панели воспользуемся данной функцией
        return self.name


class TeacherJob(models.Model): # Таблица «Должность» для дополнения информации по таблице "Учитель".
    # Также она нужна для подсчета количества свободного времени у преподавателя.
    name = models.CharField(
        max_length=100, 
        verbose_name='Название должности'
    )
    num_of_hours = models.IntegerField(
        null=True,
        verbose_name='Количество часов работы (расчет за один семестр)'
    )

    class Meta:
        verbose_name = 'Должность' # Придадим имя классу для админ-панели
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name

class Teacher(models.Model): # Основная таблица «Учитель». Нужна для подготовки данных для демонстрации работоспособности приложения (распределить учебную нагрузку). Также является расширенной версией таблицы «Пользователь».
    is_busy = models.BooleanField(
        verbose_name='Занят ли преподаватель?',
        default=False,
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
        null=True,
    )
    middle_name = models.CharField(
        max_length=100,
        verbose_name='Отчество',
        null=True,
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
        null=True,
    )
    date_of_birth = models.DateField() # Поле "Дата рождения". Дата рождения преподавателя
    academic_degree = models.ForeignKey( # Связь с таблицей "Ученая степень". Нужно показать, какая у преподавателя ученая степень
        AcademDegree,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    teacher_job = models.ForeignKey(
        TeacherJob, # Связь с таблицей "Должность". Нужно показать, какая у преподавателя должность
        on_delete=models.SET_NULL, # Если не будет больше такой должности, то преподаватель в программе останется без должности
        blank=True,
        null=True,
    ) 
    job_exp = models.IntegerField(
        verbose_name='Стаж',
    )
    user = models.OneToOneField(
        User, # Связь с таблицей "Должность". Нужно показать, какая у преподавателя должность
        on_delete=models.CASCADE, # В случае удаления пользователя пропадает и информация о преподавателе
        null=True,
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        blank=True,
    )
    location = models.CharField(
        max_length=300,
        verbose_name='Место жительства',
        null=True,
    )

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

    def __str__(self):
        return f"{self.pk}. {self.first_name} {self.middle_name} {self.last_name} ({self.date_of_birth})"


class Subject(models.Model): # Таблица «Предметная область», где ведется расчет для преподавателя
    name = models.CharField(
        max_length=50,
        verbose_name='Название предмета'
    )
    num_of_weeks = models.IntegerField(
        verbose_name='Количество учебных недель',
        null=True,
    )
    num_of_sub_in_week = models.IntegerField(
        verbose_name='Количество предметов в неделю',
        null=True
    )

    class Meta:
        verbose_name = "Предметная область"
        verbose_name_plural = "Предметная область"

    def __str__(self):
        return f"{self.name} ({self.num_of_hours_semester()} ч.)" # Отображаем количество часов 

    def num_of_hours_semester(self): # Предназначена для подсчета количества часов предмета, предназначенное для семестра
        return (self.num_of_weeks)*(self.num_of_sub_in_week) if (self.num_of_weeks is not None) and (self.num_of_sub_in_week is not None) else 0


class GroupClass(models.Model): # Таблица «Группа студентов» для выбора
    name = models.CharField(
        max_length=50,
        verbose_name="Имя группы",
    )
    is_finished = models.BooleanField() # Информация о выпуске 

    class Meta: 
        verbose_name = "Группа студентов"
        verbose_name_plural = "Группа студентов"

    def __str__(self):
        return self.name


class StudyWorkload(models.Model): # Объединяющая таблица «Учебная нагрузка», в которой и будет хранится информация в формате «Такой-то преподаватель проводит занятия по такому-то предмету с такой-то группой».
    teacher = models.ForeignKey(
        Teacher, # Первоначально нагрузку нужно связать с преподавателем
        on_delete=models.SET_NULL,   
        null=True,     
    )
    subject = models.ForeignKey(
        Subject, # Свяжем нагрузку также с предметом
        on_delete=models.SET_NULL,
        null=True,
    )
    group = models.ForeignKey(
        GroupClass, # Отобранная группа студентов
        on_delete=models.SET_NULL,
        null=True,
    )
    sub_type = models.CharField(
        verbose_name='Вид проводимого занятия', 
        null=True, max_length=100,
        choices=SUBJECT_TYPE_CHOICES)

    class Meta:
        verbose_name = "Учебная нагрузка"
        verbose_name_plural = "Учебная нагрузка"

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name} - {self.subject} - {self.group}"

    def check_free_time(self): # Делаем проверку на свободное время
        free_time = self.teacher.teacher_job.num_of_hours 
        sub_assigned_set = StudyWorkload.objects.filter(
            teacher_id=self.teacher.id, 
        )
        for sub in sub_assigned_set:
            free_time -= sub.subject.num_of_hours_semester()
        if free_time < 0: # В случае обнаружения того факта, что у преподавателя нет свободного времени, обновляем флаг занятости
            Teacher.objects.filter(id=self.teacher.id).update(is_busy=True)
        else: # Иначе даем информацию, что преподаватель вновь свободен. Например, в случае освобождения от одной из нагрузок
            Teacher.objects.filter(id=self.teacher.id).update(is_busy=False)
        return free_time 
