from rexec import FileWrapper
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .forms import UserForm


@login_required(login_url='/accounts/login/')
def index(request):
    return HttpResponseRedirect('/dashboard/')


@login_required(login_url='/accounts/login/')
def dashboard(request):
    return render(request, 'index.html', {'user': request.user})


def register(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            new_user = authenticate(username=user_form.cleaned_data['username'],
                                    password=user_form.cleaned_data['password'], )
            login(request, new_user)
            return HttpResponseRedirect('/')
        else:
            print user_form.errors
    return render(request, 'login.html', {})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your account has been disabled.")
        else:
            # print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'login.html', {})


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def upload_files(request):
    from .serializers import UserFileSerializer, FileDetailSerializer
    data = request.data
    print request.user, request.user.id
    files = [{'file': user_file, 'type': data['type']} for user_file in list(request.FILES.values())]
    file_serializer = UserFileSerializer(data={"files": files}, context={'user_id': request.user.id})
    if file_serializer.is_valid():
        files = file_serializer.save()
        response_serializer = FileDetailSerializer(files)
        return Response(data=response_serializer.data, status=status.HTTP_201_CREATED)
    else:
        print file_serializer.errors
        return Response(data=file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_my_files(request):
    from .serializers import FileDetailSerializer
    from .models import UserFiles
    try:
        files = UserFiles.objects.filter(user=request.user)
        print files
        response_serializer = FileDetailSerializer(files, many=True)
        print response_serializer.data
        return Response(data=response_serializer.data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def rename_my_file(request):
    from .serializers import FileDetailSerializer
    request_serializer = FileDetailSerializer(data=request.data, context={'user_id': request.user.id})
    if request_serializer.is_valid():
        try:
            request_serializer.save()  # Creates instance
            changed_file = request_serializer.save()  # Updates instance
            response_serializer = FileDetailSerializer(changed_file)
            return Response(data=response_serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(data=request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def delete_my_files(request):
    from .serializers import UserFileRequestSerializer
    from copy import deepcopy
    data = deepcopy(request.data)
    print data
    request_serializer = UserFileRequestSerializer(data=request.data, context={'user_id': request.user.id}, many=True)
    if request_serializer.is_valid():
        try:
            for user_file in request_serializer.validated_data:
                if user_file['file'].user == request.user:
                    user_file['file'].delete()
            print data
            return Response(data=data, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(data=request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def debug_request(request):
    print request.data
    try:
        print list(request.FILES.values())
    except:
        pass
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def scheduler(request):
    from scheduler.utils import select_slave_node, health_check
    from .serializers import ScheduleSerializer, ScheduleResponseSerializer, ExecutionRequestSerializer
    from .types import ExecutionRequestType
    import requests
    print request.data
    request_serializer = ScheduleSerializer(data=request.data, context={'user_id': request.user.id})
    if request_serializer.is_valid():
        try:
            schedule = request_serializer.save()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        node = select_slave_node()
        # node = Node.objects.get(host=True)
        schedule.node = node
        files = [(schedule.executable.name.split('/')[-1], schedule.executable.file.file),
                 (schedule.input_file.name.split('/')[-1], schedule.input_file.file.file)]
        url = "http://%s:%d/execute/" % (node.ip, node.port)
        print files
        execution_request_serializer = ExecutionRequestSerializer(
            ExecutionRequestType(schedule_id=schedule.id, time_limit=schedule.time_limit,
                                 memory_limit=schedule.memory_limit))
        r = requests.post(url, files=files, data=execution_request_serializer.data)
        if r.status_code == 202:
            return Response(data=ScheduleResponseSerializer(schedule).data, status=status.HTTP_201_CREATED)
        else:
            scheduler.status = 'F'
            schedule.save()
            health_check(node)
            print "error" + str(r.status_code)
            return Response({'msg': 'UNABLE to deliver the job to slave'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_my_schedules(request):
    from .serializers import ScheduleResponseSerializer
    from .models import Schedule
    try:
        schedules = Schedule.objects.filter(user=request.user)
        response_serializer = ScheduleResponseSerializer(schedules, many=True)
        print response_serializer.data
        return Response(data=response_serializer.data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def diff_files(request):
    from difflib import Differ
    differ = Differ()
    from .serializers import DiffRequestSerializer, DiffSerializer
    request_serializer = DiffRequestSerializer(data=request.data, context={'user_id': request.user.id})
    if request_serializer.is_valid():
        try:
            old_file, new_file = request_serializer.get_files()
            lines = list(differ.compare(old_file.splitlines(1), new_file.splitlines(1)))
            lines_diff = []
            for line in lines:
                if line[0] == ' ':
                    delta = 0
                elif line[0] == '+':
                    delta = 1
                elif line[0] == '-':
                    delta = -1
                else:
                    continue
                lines_diff.append({"delta": delta, "line": line.rstrip('\n')})
            response_serializer = DiffSerializer(data=lines_diff, many=True)
            if response_serializer.is_valid():
                return Response(data=response_serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response(data=response_serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(data=request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def download_file(request):
    import os
    payload = request.query_params
    print payload
    file_id = payload["file_id"]
    from ui.models import UserFiles
    try:
        file_real = UserFiles.objects.get(id=file_id)
        if file_real.user == request.user:
            wrapper = FileWrapper(file_real.file.file)
            response = HttpResponse(wrapper, content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(file_real.name)
            response['Content-Length'] = file_real.file.size
            return response
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
