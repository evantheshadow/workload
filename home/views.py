from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from .forms import (
    CreateNewTutorList, CreateNewWorkload, ViewProfileForm
)
from .models import *

@login_required(login_url='/login/') 
def home(response): # Перенаправление на домашнюю страницу
    return render(response, "main/home.html", {"teachers": "Нет информации"})

def teachers_list(response): # Переход на список преподавателей
    t_list = Teacher.objects.all()
    study_list = StudyWorkload.objects.all() 
    for tutor in t_list: # Смотрим информацию по всем преподавателям
        study_list = StudyWorkload.objects.filter(teacher_id=tutor.id)
        if study_list.exists(): # Проверяем, сколько свободных часов у преподавателя еще осталось
            for study in study_list:
                tutor.rest_free_time = study.check_free_time()
        else:            
            tutor.rest_free_time = tutor.teacher_job.num_of_hours
        # Если учебная нагрузка не назначалась ранее, то ставится количество часов, предназначенное
        # по должности согласно математической модели
    return render(response, "main/tutorList.html", {'teachers': t_list})

def create_tutor(response): # Добавление преподавателя
    error_list = []
    if response.method == "POST":
        new_object = CreateNewTutorList(response.POST)
        if new_object.is_valid(): # Проверка правильности ввода полей для добавления преподавателя
            print('Успешно')
            Teacher.objects.create(
                first_name = new_object.cleaned_data["name"],
                last_name = new_object.cleaned_data["surname"],
                academic_degree_id = new_object.cleaned_data["academ"].id,
                teacher_job_id = new_object.cleaned_data["job"].id,
                middle_name=new_object.cleaned_data["middle_name"],
                date_of_birth=new_object.cleaned_data["date_of_birth"],
                job_exp=new_object.cleaned_data["job_exp"],
                user_id=new_object.cleaned_data["user_choice"].id
            )
            return HttpResponseRedirect("/list_of_tutors")
        else: # Если же неправильно введены поля, то приложение выведет уведомление об ошибке
            print('Ошибка 2.')
            print(new_object.cleaned_data)
            print(new_object.errors)
            for field in new_object.errors:    
               error_list.append((new_object.errors[field].as_text())[2::]) # Обработка текста ошибки для уведомлений
            new_object = CreateNewTutorList()
    else:
        new_object = CreateNewTutorList()
    return render(response, "create/tutor.html", { # Выходим на страницу списка преподавателей 
        'form': new_object, 
        'error_list': error_list, # Список ошибок 
        'count': len(error_list), # Количество ошибок
    })

def study_work_list(response): # Учебная нагрузка
    if response.user.is_superuser: # Для администратора показывается вся учебная нагрузка
        work_list = StudyWorkload.objects.all()
    else: # Если же нет прав администратора, то выводится информация о учебной нагрузке преподавателя
        try:
            current_teacher = Teacher.objects.get(user_id=response.user.id)
            work_list = StudyWorkload.objects.filter(teacher_id=current_teacher.id)
        except: 
            work_list = []
    return render(response, "main/workList.html", {'work': work_list})

def create_workload(response): # Назначение учебной нагрузки
    error_list = []
    if response.method == "POST":
        new_object = CreateNewWorkload(response.POST)
        if new_object.is_valid():
            cur_teacher = new_object.cleaned_data["cur_teacher"]
            cur_subject = new_object.cleaned_data["cur_subject"]
            cur_group = new_object.cleaned_data["cur_group"]
            cur_sub_type = new_object.cleaned_data["sub_type"]
            StudyWorkload.objects.create( # Назначение учебной нагрузки на учителя
                teacher_id=cur_teacher.id,
                subject_id=cur_subject.id,
                group_id=cur_group.id,
                sub_type=cur_sub_type,
            )
            return HttpResponseRedirect("/list_of_work")
        else:   
            for field in new_object.errors: # Вывод ошибок в случае некорректности введенных данных
               error_list.append((new_object.errors[field].as_text())[2::])
            new_object = CreateNewWorkload()
    else:
        new_object = CreateNewWorkload()
    return render(response, "create/workload.html", {
        'form': new_object,
        'error_list': error_list, 
    })

def delete_workload(response, id):
    work = get_object_or_404(StudyWorkload, id=id)  # При нажатии на "карточку" с нагрузкой выбирается определенная нагрузка.

    if response.method == 'POST':        # Если кнопка была нажата,
        work.delete()                     # то преподаватель освобождается от учебной нагрузки (количество свободных часов увеличится).
        work.check_free_time()
        return HttpResponseRedirect('/list_of_work/') # В конце переходим на начальную страницу "Учебная нагрузка".

    return render(response, 'main/workList.html', {'work': work})

def get_profile_info(response): # Страница личного профиля
    isUserTeacher = False 
    view_info = ViewProfileForm(response.GET)
    current_user_info = User.objects.get(id=response.user.id)
    academ_list = AcademDegree.objects.all()
    teacher_job_list = TeacherJob.objects.all()
    current_teach_info = None
    try:
        current_teach_info = Teacher.objects.get(user_id=current_user_info.id)
        view_info = ViewProfileForm(initial = {
            'date_of_birth': current_teach_info.date_of_birth if current_teach_info.date_of_birth else None,
            'academ_degrees': current_teach_info.academic_degree.id if current_teach_info.academic_degree else None, 
            't_jobs': current_teach_info.teacher_job.id if current_teach_info.teacher_job else None
        })
        isUserTeacher = True
    except Teacher.DoesNotExist:
        current_teach_info = None
    return render(response, "main/profile.html", {
        'form': view_info,
        'isThatUserTeacher': isUserTeacher,
        'user_info': current_user_info,
        'work_info': current_teach_info,
        'academ_dropdown_list': academ_list,
        'teacher_job_dropdown_list': teacher_job_list, 
    })

def save_changed_profile_info(response):
    if response.method == "POST":
        my_email = response.POST.get("email", "") 
        User.objects.filter(id=response.user.id).update(
            email=my_email,
        )
        profile_info = ViewProfileForm(response.POST)
        if profile_info.is_valid():
            if Teacher.objects.filter(user_id=response.user.id).exists():
                Teacher.objects.filter(user_id=response.user.id).update(
                    first_name = response.POST.get("name", ""),
                    last_name = response.POST.get("surname", ""),
                    middle_name = response.POST.get("middle_name", ""),
                    phone_number = response.POST.get("phone_number", ""),
                    academic_degree = profile_info.cleaned_data["academ_degrees"].id,
                    teacher_job = profile_info.cleaned_data["t_jobs"].id,
                    date_of_birth = profile_info.cleaned_data["date_of_birth"],
                    location = response.POST.get("location", ""),
                )
        return HttpResponseRedirect('/profile/')
    else:
        profile_info = ViewProfileForm()
    return render(response, "create/workload.html", {'form': profile_info})

def info(response):
    return render(response, "main/instruction.html", {})