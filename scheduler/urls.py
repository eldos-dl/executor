from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stats/$', views.get_stats, name='stats'),
    url(r'^follow/me/$', views.follow_me, name='follow_me'),
    url(r'^follower/confirm/$', views.follow_me, name='follower_confirm'),
    url(r'^execute/', views.execute, name='executed'),
    url(r'^output/', views.update_output, name='output'),
    url(r'^lead/', views.lead_nodes, name='lead'),


]
