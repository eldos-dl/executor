from django.contrib import admin

from .models import Node, Status
# Register your models here.
admin.site.register(Node)
admin.site.register(Status)