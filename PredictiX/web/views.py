from django.shortcuts import render, redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from ml import Interface
from .models import MachineRecord

import warnings
warnings.filterwarnings("ignore")

# Create your views here.


def home(request):
    return render(request, "web/home.html")


@csrf_exempt
# @login_required(login_url='')
def predict(request):
    if request.method == "POST":
        # input
        air_temp = request.POST["air_temp"]
        process_temp = request.POST["process_temp"]
        rotational_speed = request.POST["rotational_speed"]
        torque = request.POST["torque"]
        tool_wear = request.POST["tool_wear"]
        quality = request.POST["quality"]
        name = request.POST["machine_name"]
        # auth

        list = [[air_temp, process_temp,
                 rotational_speed, torque,
                 tool_wear, quality]]

        preds = Interface.predict(list)

        # For android
        if request.POST.get("client", "web") == "android":
            user = request.POST["user"]
            password = request.POST["password"]
            request.user = authenticate(username=user, password=password)
            record = MachineRecord(name=name, user=request.user, air_temp=air_temp,
                                   process_temp=process_temp, rotational_speed=rotational_speed,
                                   torque=torque, tool_wear=tool_wear,
                                   quality=quality, predictions=preds.tolist())
            record.save()
            return HttpResponse(record)

        # For Web
        record = MachineRecord(name=name, user=request.user, air_temp=air_temp,
                               process_temp=process_temp, rotational_speed=rotational_speed,
                               torque=torque, tool_wear=tool_wear,
                               quality=quality, predictions=preds.tolist())
        record.save()
        return HttpResponse(record)

# Auth part

# TODO:S Solve csrf issue


@csrf_exempt
def loginUser(request):
    if request.method == "POST":
        username = request.POST["loginusername"]
        password = request.POST["loginpass"]
        client = request.POST.get("client", "web")

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if client == "android":
                return HttpResponse(user)
            return redirect("Home")
        else:
            if client == "android":
                return HttpResponse("Failed!!")
            return redirect("Login")

    else:
        print(request.GET)
        return render(request, "web/login.html")

from django.core import serializers

def predictions(request):
    # For Android
    if request.META.get("HTTP_CLIENT","web")=="android":
        user = request.META.get("HTTP_USER")
        pass1 = request.META.get("HTTP_PASS")
        request.user = authenticate(username=user,password=pass1)
        data = MachineRecord.objects.filter(user=request.user)
        log = serializers.serialize("json",data)
        return HttpResponse(log)
    # For Web
    data = MachineRecord.objects.filter(user=request.user)
    log = serializers.serialize("json",data)
    return HttpResponse(log)

def logoutUser(request):
    logout(request)
    print("Logged out!")
    return redirect("Home")


def genName(name):
    name = name.split(" ")
    if len(name) == 2:
        return name[0], name[1]
    elif len(name) == 3:
        return name[0], name[2]
    else:
        return name[0], ""


def signupUser(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        name = str(name).strip()

        fName, lName = genName(name)

        if not pass1 == pass2:
            return redirect("Signup")

        user = User.objects.create_user(username=email,
                                        first_name=fName,
                                        last_name=lName,
                                        password=pass1)
        if user:
            user.save()
            print("User created succesfully!")
            return redirect("Home")
        else:
            print("User already exists ")
            return redirect("Signup")

    else:
        return render(request, "web/signup.html")
