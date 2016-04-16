from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/', views.user_login, name='login'),
    url(r'^accounts/signup/', views.register, name='signup'),
    url(r'^accounts/logout/', views.user_logout, name='logout'),
    url(r'^upload/$', views.upload_files, name='upload'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^my_files/', views.get_my_files, name='my_files'),
    url(r'^rename_file/', views.rename_my_file, name='rename_my_file'),
    url(r'^delete_files/', views.delete_my_files, name='delete_my_files'),
    url(r'^my_schedules/$', views.get_my_schedules, name='my_schedules'),
    url(r'^request/$', views.debug_request, name='debug'),
    url(r'^schedule/$', views.scheduler, name='schedule'),
    url(r'^diff/$', views.diff_files, name='diff'),
]
