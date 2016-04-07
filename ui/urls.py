from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^accounts/login/', views.user_login, name='login'),
    url(r'^accounts/signup/', views.register, name='signup'),
    url(r'^accounts/logout/', views.user_logout, name='logout'),

]