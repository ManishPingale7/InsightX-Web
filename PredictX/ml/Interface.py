import joblib
import tensorflow as tf
from keras.models import load_model
from collections import Counter
import numpy as np

# Label mapping
# 0-> No Failure, 1-> Power, 2-> Tool, 3-> Overstrain, 4-> Heat
# {'B': 0, 'I': 1, 'IB': 2, 'IO': 3, 'N': 4, 'O': 5, 'OB': 6}


class Interface:
    def __init__(self):
        self.cond_model = load_model("ML/INSIGHTX_ANN.h5")

    @staticmethod
    def predict(data, model):
        if model == "0":
            model = joblib.load("ML/BalancedBaggin.joblib")
        else:
            model = joblib.load("ML/BalancedRandomForest.joblib")

        preds = model.predict_proba(data)
        return preds

    def diagnose(self, vib_data):
        mapping = {0: 'B', 1: 'I',  2: 'IB',
                   3: 'IO', 4: 'N', 5: 'O',  6: 'OB'}
        preds = []
        for i in vib_data:
            i = i.astype(np.float64)
            op = self.cond_model.predict(i)
            preds.append(np.argmax(op))

        stats = Counter(preds).most_common()
        prob = {}
        print(stats)
        for i in stats:
            prob[mapping[i[0]]] = ((i[1])/len(vib_data))*100
        return prob
