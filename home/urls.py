from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path('', views.home, name = "home"),
    path('info/', views.info, name="info"),
    path('profile/', views.get_profile_info, name="myAccount"),
    path('profile/save/', views.save_changed_profile_info, name="myAccountInfo"),
    path('list_of_tutors/', views.teachers_list, name="teacherList"),
    path('list_of_work/', views.study_work_list, name="workList"),
    path('create/tutor/', views.create_tutor, name="createTutor"),
    path('create/study_work/', views.create_workload, name="createWork"),
    path('delete/study_work/<int:id>', views.delete_workload, name='deleteWork'),
    # path("<int:id>/", views.index, name="index"),
] 
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)