import json
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from web.views import gen_name
from django.contrib.auth.models import User
from ml import Interface
from web.models import MachineRecord
from django.core import serializers
from utils.serializers import records_serializer


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        username = request.POST["loginusername"]
        password = request.POST["loginpass"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse('{"status":"SUCCESS"}', status=200, safe=False)
        return JsonResponse('{"status":"FAILED"}', status=401, safe=False)


@csrf_exempt
# Client side will take care of validations
def signup_user(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        pass1 = request.POST["pass1"]
        name = str(name).strip()

        f_name, l_name = gen_name(name)

        if (User.objects.filter(username=email).exists()):
            return JsonResponse("Username already exists", status=409, safe=False)

        user = User.objects.create_user(username=email,
                                        first_name=f_name,
                                        last_name=l_name,
                                        password=pass1)
        if user:
            user.save()
            return JsonResponse("User successfully created", status=200, safe=False)
        return JsonResponse("Failed to create user", status=401, safe=False)


# Adding record

def predict(request):
    # Input
    print((request.body))
    print("REQUEST: ", json.loads(request.body.decode('utf-8')))
    body = json.loads(request.body.decode('utf-8'))
    air_temp = body["air_temp"]
    process_temp = body["process_temp"]
    rotational_speed = body["rotational_speed"]
    torque = body["torque"]
    tool_wear = body["tool_wear"]
    quality = body["quality"]
    machine_name = body["machine_name"]
    algo = body["model"]

    list = [[air_temp, process_temp,
             rotational_speed, torque,
             tool_wear, quality]]

    preds = Interface.predict(list, algo)

    # Auth
    user = body["user"]
    password = body["password"]
    request.user = authenticate(username=user, password=password)

    record = MachineRecord(machine_name=machine_name, user=request.user, air_temp=air_temp,
                           process_temp=process_temp, rotational_speed=rotational_speed,
                           torque=torque, tool_wear=tool_wear,
                           quality=quality, predictions=preds.tolist())
    record.save()
    record = records_serializer(record)

    return JsonResponse(record, safe=False)


@csrf_exempt
def all_records(request):

    # Return All Records
    if request.method == "GET":
        user = request.META.get("HTTP_USER")
        pass1 = request.META.get("HTTP_PASS")
        request.user = authenticate(username=user, password=pass1)
        data = MachineRecord.objects.filter(user=request.user)
        # data = MachineRecord.objects.all()
        log = records_serializer(data)
        return JsonResponse(log, safe=False)

    # Add Single Record
    elif request.method == "POST":
        return predict(request)


@csrf_exempt
def single_record(request, id):

    # Get a single record
    if request.method == "GET":
        record = MachineRecord.objects.filter(id=id).first()
        if record:
            return JsonResponse(records_serializer(record), safe=False, status=200)
        return JsonResponse("Record not found!", safe=False, status=404)

    # Delete a single record
    elif request.method == "DELETE":
        record = MachineRecord.objects.filter(id=id).first()
        if record:
            record.delete()
            return JsonResponse("Deleted Successfully", safe=False, status=200)
        return JsonResponse("Record not found!", safe=False, status=404)
