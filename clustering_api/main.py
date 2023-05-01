from os import environ
from flask import Flask, jsonify,request
from k_means_constrained import KMeansConstrained
import numpy as np

server = Flask(__name__)

server.config['APP_NAME'] = environ.get("APP_NAME")
server.config['FLASK_ENV'] = environ.get("FLASK_ENV")
server.config['DEBUG'] = environ.get("FLASK_DEBUG")
server.config['SECRET_KEY'] = environ.get("SECRET_KEY")

def str_to_list_of_float(value):
    if value == 'null':
        return []
    lst = value.split(',')
    return [val.replace(' ','').replace('"','') for val in lst]

@server.route("/api/", methods=['GET'])
def api_poi():
    n_clusters = int(request.args.get('n_clusters'))
    nmin = int(request.args.get('nmin'))
    nmax = int(request.args.get('nmax'))
    lon = str_to_list_of_float(request.args.get('lon'))
    lat = str_to_list_of_float(request.args.get('lat'))
    
    X = np.array([lat,lon])
    print(X)
    clf = KMeansConstrained(n_clusters=n_clusters,size_min=nmin,size_max=nmax,random_state=42)
    clf.fit_predict(X.transpose())
    labels = clf.labels_
    print(labels)
    return jsonify({"clusters": labels.tolist()})

