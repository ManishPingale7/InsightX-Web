from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

import joblib
import warnings
warnings.filterwarnings("ignore")

# Create your views here.


def home(request):
    return HttpResponse(makePrediction())


def loginUser(request):
    if request.method == "POST":
        username = request.POST["loginusername"]
        password = request.POST["loginpass"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            print("Successfully logged in")
            return redirect("Home")
        else:
            print("Logging failed")
            return redirect("Login")

    else:
        return render(request, "web/login.html")


def logoutUser(request):
    logout(request)
    print("Logged out!")
    return redirect("Home")


def genName(name):
    name = name.split(" ")
    if len(name) ==2:
        return name[0],name[1]
    elif len(name)==3:
        return name[0], name[2]
    else:
        return name[0],""


def signupUser(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        name = str(name).strip()
        
        fName,lName = genName(name)
        
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


def makePrediction():
    model = joblib.load(".\ML\BalancedBaggin.joblib")
    preds = model.predict_proba([[29, 37, 1359, 44, 115, 0]])
    return preds
