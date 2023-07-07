from django.shortcuts import render
from django.http import HttpResponse
import joblib

# Create your views here.

def home(request):
    print(makePrediction())
    return HttpResponse(makePrediction())


def makePrediction():
    model = joblib.load(".\ML\BalancedBaggin.joblib")
    print(model)
    preds = model.predict_proba([[29.85 ,37.85 ,1359.00 ,44.20 ,115.00 ,0.00]])
    return preds