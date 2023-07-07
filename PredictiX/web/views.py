from django.shortcuts import render
from django.http import HttpResponse
import joblib
import warnings
warnings.filterwarnings("once")

# Create your views here.


def home(request):
    return HttpResponse(makePrediction())


def makePrediction():
    model = joblib.load(".\ML\BalancedBaggin.joblib")
    preds = model.predict_proba([[29, 37, 1359, 44, 115, 0]])
    return preds
