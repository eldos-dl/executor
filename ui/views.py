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
def upload_files(request, format=None):
    from .serializers import UserFileSerializer
    data = request.data
    print request.user, request.user.id
    files = [{'file': user_file, 'type': data['type']} for user_file in list(request.FILES.values())]
    file_serializer = UserFileSerializer(data={"files": files}, context={'user_id': request.user.id})
    if file_serializer.is_valid():
        file_serializer.save()
        return Response(data={"created": len(files)}, status=status.HTTP_201_CREATED)
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
def debug_request(request):
    print request.data
    try:
        print request.FILES.values()
    except:
        pass
    return Response(status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def get_user_files(request):
    pass