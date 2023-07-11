from django.contrib.auth import authenticate,login
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.views import gen_name
from django.contrib.auth.models import User
from ml import Interface
from web.models import MachineRecord
from django.core import serializers
from utils.serializers import predictions_serializer


@csrf_exempt
def login_user(request):
    if request.method =="POST":
        username = request.POST["loginusername"]
        password = request.POST["loginpass"]

        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return HttpResponse(user)
        return HttpResponse("Login Failed")

@csrf_exempt
def signup_user(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        name = str(name).strip()

        f_name, l_name = gen_name(name)

        if not pass1 == pass2:
            return HttpResponse("Passwords do not match")

        user = User.objects.create_user(username=email,
                                        first_name=f_name,
                                        last_name=l_name,
                                        password=pass1)
        if user:
            user.save()
            return HttpResponse(user)
        return HttpResponse("Failed to create user")

@csrf_exempt
def predict(request):
    if request.method == "POST":
        # Input
        air_temp = request.POST["air_temp"]
        process_temp = request.POST["process_temp"]
        rotational_speed = request.POST["rotational_speed"]
        torque = request.POST["torque"]
        tool_wear = request.POST["tool_wear"]
        quality = request.POST["quality"]
        name = request.POST["machine_name"]

        list = [[air_temp, process_temp,
                 rotational_speed, torque,
                 tool_wear, quality]]

        preds = Interface.predict(list)

        #Auth
        user = request.POST["user"]
        password = request.POST["password"]
        request.user = authenticate(username=user, password=password)

        record = MachineRecord(name=name, user=request.user, air_temp=air_temp,
                                   process_temp=process_temp, rotational_speed=rotational_speed,
                                   torque=torque, tool_wear=tool_wear,
                                   quality=quality, predictions=preds.tolist())
        record.save()
        record = serializers.serialize("json",[record])

        return HttpResponse(record)        

@csrf_exempt
def predictions(request):
    user = request.META.get("HTTP_USER")
    pass1 = request.META.get("HTTP_PASS")
    request.user = authenticate(username=user,password=pass1)
    data = MachineRecord.objects.filter(user=request.user)
    log = predictions_serializer(data)
    return JsonResponse(log,safe=False)