import joblib

def predict(list):
    model = joblib.load("ML/BalancedBaggin.joblib")
    preds = model.predict_proba(list)
    return preds