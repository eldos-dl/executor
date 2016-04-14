from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/', views.user_login, name='login'),
    url(r'^accounts/signup/', views.register, name='signup'),
    url(r'^accounts/logout/', views.user_logout, name='logout'),
    url(r'^upload/$', views.upload_files, name='upload'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^myfiles/', views.get_my_files, name='my_files'),
    url(r'^request/', views.debug_request, name='debug'),


]