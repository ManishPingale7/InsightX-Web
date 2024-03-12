from django.core import serializers
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import csv
import io
import os
import numpy as np
import pandas as pd

from ml.Interface import Interface
from .models import MachineRecord,MonitorRecord


import warnings
warnings.filterwarnings("ignore")

# Create your views here.


def home(request):
    return render(request, "web/home.html")


def monitoring(request):
    return render(request, "web/bearings_prediction.html")


def explore(request):
    return render(request, "web/explore.html")


def plots(request):
    return render(request, "web/graph.html")


def delete_record(request, id):
    if request.method == "DELETE":
        record = MachineRecord.objects.filter(id=id)
        if record:
            record[0].delete()
            return HttpResponse("true")
        return HttpResponse("false")

def condition(request,id):
    record=MonitorRecord.objects.filter(id=id,user=request.user)
    if record:
        record=serializers.serialize('json',record)
        return render(request,"web/condition.html",{"record":record})
    return redirect("Home")


def dashboard(request, id):
    record = MachineRecord.objects.filter(id=id, user=request.user)
    if record:
        record = serializers.serialize('json', record)
        return render(request, "web/dashboard.html", {"record": record})
    return redirect("Home")


def process_file(file, power):
    data_set = file.read().decode("latin-1")
    df = pd.read_csv(io.StringIO(data_set))

    # Keeping only first column
    if (df.shape[1] > 1):
        cols = df.columns
        df = df[cols[0]]

    if (not df.shape[0] > 4000):
        return -1

    win_l = 4000
    stride = 800
    X = []
    for j in np.arange(0, len(df)-(win_l), stride):
        win = df.iloc[j:j+win_l, :].values
        win = win.reshape((1, -1))
        X.append(win)

    # Considering 10% from start and end
    last_rec = int((len(X)*0.1))
    X = X[:last_rec]+X[-last_rec:]
    for i in range(0, len(X)):
        X[i] = np.column_stack((X[i], power))
    return X



@login_required
def diagnose(request):
    if request.method == "POST" and request.FILES["vib_file"]:
        file = request.FILES["vib_file"]
        if not file.name.endswith(".csv"):
            return HttpResponse("Please use csv format only ")
        res = process_file(file, request.POST['power'])
        
        if res == -1:
            return HttpResponse("CSV File should contain atleast 5000 values")
        else:        
            name=request.POST["machine_name"]
            interface = Interface()
            result=interface.diagnose(res)
            print("In view:",result)
            rec=MonitorRecord(
                machine_name=name,user=request.user,predictions=result
                )
            rec.save()
            return redirect("Condition",id=rec.id)
        
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

        preds = Interface.predict(list, model)
        record = MachineRecord(machine_name=name, user=request.user, air_temp=air_temp,
                               process_temp=process_temp, rotational_speed=rotational_speed,
                               torque=torque, tool_wear=tool_wear,
                               quality=quality, predictions=preds.tolist())
        record.save()
        return redirect("Dashboard", id=record.id)

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
