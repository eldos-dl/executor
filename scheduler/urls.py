from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stats/$', views.get_stats, name='stats'),
]