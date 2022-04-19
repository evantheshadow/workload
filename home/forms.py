from django import forms
from django.contrib.auth.models import User

from .models import *
from datetime import date


class DateInput(forms.DateInput):
    input_type = 'date' # Сделаем виджет, в котором будет вводиться дата


class CreateNewTutorList(forms.Form):
    class Meta:
        widgets = {
            'date_of_birth': DateInput(),
        }

    name = forms.CharField(label="Имя", max_length=100)
    middle_name = forms.CharField(label="Отчество", max_length=100)
    surname = forms.CharField(label="Фамилия", max_length=100)
    date_of_birth = forms.DateField(label="Дата рождения", widget=DateInput)
    job_exp = forms.IntegerField(label="Стаж")
    user_choice = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'custom-select'}),
        label='Пользователь',
    )
    academ = forms.ModelChoiceField(
        queryset=AcademDegree.objects.all(),
        widget=forms.Select(attrs={'class': 'custom-select'}),
        label='Ученая степень',
    )
    job = forms.ModelChoiceField(
        queryset=TeacherJob.objects.all(),
        widget=forms.Select(attrs={'class': 'custom-select'}),
        label='Должность',
    )
    
    def clean(self):
        super(CreateNewTutorList, self).clean()
         
        # Возьмем данные из выбранных ранее сведений
        job_exp = self.cleaned_data.get('job_exp')
        date_of_birth = self.cleaned_data['date_of_birth']
        choosed_user = self.cleaned_data.get('user_choice')

        if Teacher.objects.filter(user_id=choosed_user.id).exists():
            self.errors['user_error'] = self.error_class([
                'Пользователь, которого Вы хотите прикрепить, уже прикреплен к другому преподавателю. Выберите другого пользователя.'])
 
        # Делаем условия на ошибки в зависимости от определенного значения
        if job_exp < 0:
            self.errors['exp_error'] = self.error_class([
                'Стаж не может быть отрицательным числом.'])
        elif job_exp > 100:
            self.errors['exp_error'] = self.error_class([
                'Превышен максимум стажа для данного приложения: 100 лет.'])
        
        print(f"self.calculate_age(date_of_birth) > (int(job_exp): {self.calculate_age(date_of_birth) > (int(job_exp))}")
        print(f"self.calculate_age(date_of_birth) < (int(job_exp) - 21) and (self.calculate_age(date_of_birth) > 0): {self.calculate_age(date_of_birth) < (int(job_exp) - 21) and (self.calculate_age(date_of_birth) > 0)}")
        if self.calculate_age(date_of_birth) < 0:
            self.errors['date_error'] = self.error_class([
                'Дата рождения должна быть раньше, чем нынешнее время.'])
        elif self.calculate_age(date_of_birth) < (int(job_exp) - 21) and (self.calculate_age(date_of_birth) > 0):
            self.errors['date_error'] = self.error_class([
                'Стаж может отсчитываться после трудоустройства, в условия которого необходимо иметь образование не ниже бакалавра.'])
        # return any errors if found
        return self.cleaned_data

    def calculate_age(self, birth_date):
        today = date.today() # Для начала возьмем сегодняшний день
    # Данная булевская переменная проверяет, наступил ли день рождения в этом году или еще нет.
    # Выдает значение 1 (True) или 0 (False).
        one_or_zero = ((today.month, today.day) < (birth_date.month, birth_date.day))
    # Проверяем разность между нынешним годом и годом рождения
        year_difference = today.year - birth_date.year
    # Для полного вычисления возраста вычитаем из разницы между нынешним годом
    # и днем рождения булевскую переменную, которая конвертируется в 1 или 0.
        age = year_difference - one_or_zero
        print(f'Age: {age}')
        return age


class CreateNewWorkload(forms.Form): # Форма назначения учебной нагрузки
    cur_teacher = forms.ModelChoiceField( #Выбор преподавателя
        queryset=Teacher.objects.exclude(is_busy=True), # Исключаем тех преподавателей из списка, которые уже заняты (0 и меньшее количество свободных часов)
        widget=forms.Select(attrs={'class': 'custom-select'}),
        label="Преподаватель"
    )
    cur_subject = forms.ModelChoiceField( # Выбор предмета
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'custom-select'}),
        label='Предметная область'
    )
    cur_group = forms.ModelChoiceField( # Выбор группы студентов
        queryset=GroupClass.objects.all(),
        widget=forms.Select(attrs={'class': 'custom-select'}),
        label='Группа студентов'
    )
    sub_type = forms.ChoiceField( # Выбор вида занятий
        label="Вид занятия",
        choices=SUBJECT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=False,
    )

    def clean(self): # Проверка правильности введенных данных
        super(CreateNewWorkload, self).clean()
        current_teacher = self.cleaned_data.get('cur_teacher')
        subject = self.cleaned_data.get('cur_subject')

        if self.check_free_time(current_teacher) < 0: # Если количество свободных часов меньше 0, то выдаст уведомление о выборе другого преподавателя.
            self.errors['free_time_error'] = self.error_class([
                f'Преподаватель {current_teacher.last_name} {current_teacher.first_name} {current_teacher.middle_name} уже занят. Выберите другого.'])
        elif self.check_free_time(current_teacher) < subject.num_of_hours_semester(): # Если предмет по количеству часов больше, чем количество свободных часов преподавателя, то выдаст также уведомление о выборе другого преподавателя.
            self.errors['free_time_error'] = self.error_class([
                f"Преподаватель {current_teacher.last_name} {current_teacher.first_name} {current_teacher.middle_name} не имеет достаточное количество свободных часов - {self.check_free_time(current_teacher)} часов. Выберите другого."
            ])

    def check_free_time(self, teacher): # Проверка на количество свободных часов преподавателя
        free_time = teacher.teacher_job.num_of_hours 
        sub_assigned_set = StudyWorkload.objects.filter(
            teacher_id=teacher.id, 
        ) # Учтем учебную нагрузку, которая была ранее назначена на преподавателя
        for assigned in sub_assigned_set:
            free_time -= assigned.subject.num_of_hours_semester() # Вычисление свободного времени согласно математической модели
        return free_time

        
class ViewProfileForm(forms.Form):
    class Meta:
        widgets = {
            'date_of_birth': DateInput(),
        }

    date_of_birth = forms.DateField(widget=DateInput, label='Дата рождения')
    academ_degrees = forms.ModelChoiceField(
        queryset=AcademDegree.objects.all(),
        label = 'Ученая степень',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )
    t_jobs = forms.ModelChoiceField(
        queryset=TeacherJob.objects.all(),
        label = 'Должность',
        widget=forms.Select(attrs={'class': 'custom-select'})
    )