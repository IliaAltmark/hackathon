"""
Author: Ilia Altmark
"""
# import os
# import pickle
import os

import pandas as pd
# import numpy as np
from flask import Flask, request, json, jsonify
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

K = 5
KNN = NearestNeighbors(n_neighbors=K + 1)
DATA = None
TRANSFORMER = None

app = Flask(__name__)


@app.route('/find_k_neighbors', methods=['POST'])
def find_k_neighbors():
    """Receiving input and returning closest neighbors"""
    input_dict = json.loads(request.get_json())

    # print(pd.json_normalize(input_dict).info())
    result = KNN.kneighbors(
        TRANSFORMER.transform(pd.json_normalize(input_dict)),
        return_distance=False)

    return jsonify(preds=result[0][1:].tolist())


@app.route('/fit_k_neighbors', methods=['POST'])
def fit_k_neighbors():
    input_dict = json.loads(request.get_json())
    global DATA
    DATA = pd.DataFrame(input_dict)

    fit_(DATA)

    return '200'


def fit_transform_(df):
    numerical = df.describe().columns.tolist()
    categorical = list(set(df.columns) - set(numerical))

    # numerical = ['age']
    # categorical = ['sex', 'diet', 'smokes', 'location', 'pets', 'speaks']

    # df_u = df[numerical.tolist() + list(categorical)].copy()
    # df_u = df[numerical + categorical].copy()

    df_u = df.copy()
    # pipeline for nominal features
    nominal_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot_encode', OneHotEncoder())])

    # pipeline for numerical features
    numerical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())])

    # uniting all pipelines for preprocessing
    transformers = ColumnTransformer([
        ('nom_enc', nominal_transformer, categorical),
        ('num_standard', numerical_transformer, numerical)
    ])

    # Transforming
    X = transformers.fit_transform(df_u)

    global TRANSFORMER
    TRANSFORMER = transformers

    return X


def fit_(df):
    X = fit_transform_(df)
    # fitting
    global KNN
    KNN = KNN.fit(X)


def main():
    port = os.environ.get('PORT')
    app.run(host='0.0.0.0', port=int(port))


if __name__ == "__main__":
    main()
