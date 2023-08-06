from django.core import serializers
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import json

from ml import Interface
from .models import MachineRecord

import warnings
warnings.filterwarnings("ignore")

# Create your views here.


def home(request):
    return render(request, "web/home.html")


def about(request):
    return render(request, "web/about.html")


def explore(request):
    return render(request, "web/explore.html")


def plots(request):
    return render(request, "web/graph.html")


def delete_record(request,id):
    if request.method == "DELETE":
        print(id)

def dashboard(request,id):
    record = MachineRecord.objects.filter(id=id,user=request.user)
    if record:
        record = serializers.serialize('json',record)
        return render(request,"web/dashboard.html",{"record":record})
    return redirect("Home")

@login_required()
def predict(request):
    if request.method == "POST":
        # Input
        model = request.POST["model"]
        air_temp = request.POST["air_temp"]
        process_temp = request.POST["process_temp"]
        rotational_speed = request.POST["rotational_speed"]
        torque = request.POST["torque"]
        tool_wear = request.POST["tool_wear"]
        name = request.POST["machine_name"]
        
        type = request.POST["type"]
        quality = -1
        if type == "low":
            quality = 0
        elif type == "high":
            quality = 2
        else:
            quality = 1

        # Auth

        list = [[air_temp, process_temp,
                 rotational_speed, torque,
                 tool_wear, quality]]

        preds = Interface.predict(list,model)
        record = MachineRecord(machine_name=name, user=request.user, air_temp=air_temp,
                               process_temp=process_temp, rotational_speed=rotational_speed,
                               torque=torque, tool_wear=tool_wear,
                               quality=quality, predictions=preds.tolist())
        record.save()
        return redirect("Dashboard",id=record.id)
    
    return render(request, "web/predict.html")

# Auth part


def login_user(request):
    if request.method == "POST":
        username = request.POST["loginusername"]
        password = request.POST["loginpass"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("Home")
        else:
            return redirect("Login")

    else:
        print(request.GET)
        return render(request, "web/login.html")


@login_required()
def history(request):
    data = MachineRecord.objects.filter(user=request.user)
    return render(request, "web/history.html", {'records': data})


def logout_user(request):
    logout(request)
    return redirect("Home")


def gen_name(name):
    name = name.split(" ")
    if len(name) == 2:
        return name[0], name[1]
    elif len(name) == 3:
        return name[0], name[2]
    else:
        return name[0], ""


def signup_user(request):
    if request.method == "POST":
        name = request.POST["fullname"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        name = str(name).strip()

        f_name, l_name = gen_name(name)

        if not pass1 == pass2:
            return redirect("Signup")

        user = User.objects.create_user(username=email,
                                        first_name=f_name,
                                        last_name=l_name,
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
