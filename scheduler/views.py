from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import json
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response


def get_stats(request):
    import psutil
    memory = psutil.virtual_memory()
    stats = {
        'memory': {
             'available': memory.available,
             'total': memory.total,
             'used_percent': memory.percent
        },
        'cpu': {
            'count': psutil.cpu_count(),
            'used_percent': psutil.cpu_percent(),
            'idle_percent': psutil.cpu_times_percent().idle
        }
    }
    return JsonResponse(stats)
