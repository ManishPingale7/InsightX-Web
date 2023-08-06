import joblib

# 0-> No Failure, 1-> Power, 2-> Tool, 3-> Overstrain, 4-> Heat 
def predict(list,model):
    if model=="0":
        model = joblib.load("ML/BalancedBaggin.joblib")
    elif model=="1":
        model = joblib.load("ML/BalancedRandomForest.joblib")

    preds = model.predict_proba(list)
    return preds