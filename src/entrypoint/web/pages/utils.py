import requests
from flask import request
from dash.exceptions import PreventUpdate
import os
import json
import pandas as pd
import dash_leaflet as dl
import numpy as np
from dash import html, ctx
import dash_bootstrap_components as dbc
#import torch
#from torch_kmeans import KMeans,ConstrainedKMeans

URL_datatourisme = os.getenv("URL")
URL_opentripmap='https://api.opentripmap.com/0.1/en/places/radius'
URL_clustering_api ='http://clustering_api'

def def_icon():
    iconBlue ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconGold ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-gold.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconRed ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconGreen ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconOrange ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconYellow ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconViolet ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-violet.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconGrey ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    iconBlack ={ 'iconUrl': 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png',
        'shadowUrl': 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        'iconSize': [25, 41],
        'iconAnchor': [12, 41],
        'popupAnchor': [1, -34],
        'shadowSize': [41, 41]
    }
    return iconBlue,iconGold,iconRed,iconGreen,iconOrange,iconYellow,iconViolet,iconGrey,iconBlack
iconBlue,iconGold,iconRed,iconGreen,iconOrange,iconYellow,iconViolet,iconGrey,iconBlack=def_icon()

def poi_icon_dt(poi):
    if "Restaurant" in poi["type"] or "'Restaurant'" in poi["type"]:
        return iconRed
    elif "Event" in poi["type"] or "Event" in poi["type"]:
        return iconViolet
    elif "Accommodation" in poi["type"] or "'Accommodation'" in poi["type"]:
        return iconGrey
    elif "CulturalSite" in poi["type"] or "'CulturalSite'" in poi["type"]:
        return iconGold
    elif "Tour" in poi["type"] or  "'Tour'" in poi["type"]:
        return iconGreen
    else:
        return iconBlack

def poi_icon_otm(kind):
    if "food" in kind:
        return iconRed
    elif "religion" in kind:
        return iconViolet
    elif "accomodations" in kind:
        return iconGrey
    elif "cultural" in kind:
        return iconGold
    elif "natural" in kind:
        return iconGreen
    elif "amusements" in kind:
        return iconGreen
    elif "architecture" in kind:
        return iconYellow
    elif "historic" in kind:
        return iconYellow
    elif "industrial_facilities" in kind:
        return iconOrange
    else:
        return iconBlack

def str_to_list(value):
    if value == 'null':
        return []
    lst = value[1:-1].split(',')
    return [val.replace(' ','').replace('"','') for val in lst]

def query_datatourisme(lat,lon,kinds,limit=500,radius=50):
    headers = {
            'Content-Type': 'application/json',
            'Cookie': request.headers.get('Cookie')
        }
    url = "{url}/api/poi?".format(url=URL_datatourisme)
    params = {
        "longitude":lon,
        "latitude":lat,
        "kinds":json.dumps(kinds,ensure_ascii=False),
        "limit":limit,
        "radius":radius
    }
    response = requests.get(url, params=params, headers=headers)
    print(response.request.url)
    df = pd.json_normalize(response.json(), record_path=['response'])
    df.to_csv("request_dt.csv")
    return df #response.json()

def query_opentripmap(lat, lon, kinds):
    itineraire_vacance_key = '5ae2e3f221c38a28845f05b632ea7c5f89c49a5ff84a17768ce137c1'
    headers = {'accept': 'application/geojson'}
    if kinds:
        params = {
            'radius': '50000',
            'lon': str(lat),
            'lat': str(lon),
            'rate': '2',
            'format': 'geojson',
            'kinds': ','.join(kinds),
            'apikey': itineraire_vacance_key,
        }
    else:
        params = {
            'radius': '50000',
            'lon': str(lat),
            'lat': str(lon),
            'rate': '2',
            'format': 'geojson',
            'apikey': itineraire_vacance_key,
        }
    response = requests.get('https://api.opentripmap.com/0.1/en/places/radius', params=params, headers=headers)
    print(response.request.url)
    #print(response.json())
    df = pd.json_normalize(response.json(), record_path=['features'])
    df.to_csv("request_otm.csv")
    return df

def poi_to_marker_2(pois,source):
    markers = []
    lats = []
    lons = []
    if source == 1:
        key_coord="location.coordinates"
        key_label="label"
        key_popup="descriptionEN"
        key_type="type"
        print(pois["type"])
    elif source == 2:
        key_coord ="geometry.coordinates"
        key_label="properties.name"
        key_popup="properties.name"
        key_type="properties.kinds"
    for i, poi in pois.iterrows():
        #print(type(poi[key_type]),poi[key_type])
        # implement the kinds to get colors!!!
        #kind = get_kind(poi[key_type],source)
        coord = poi[key_coord]
        lon = float(coord[0])
        lat = float(coord[1])
        lons.append(lon)
        lats.append(lat)
        icon = poi_icon_dt(poi) if source==1 else poi_icon_otm(poi[key_type])
        markers.append(dl.Marker(position=[lat, lon],
                                 icon=icon,
                                 children=[dl.Tooltip(poi[key_label]), 
                                           dl.Popup(poi[key_popup])],))
    ne = np.max([lats, lons], axis=1)
    sw = np.min([lats, lons], axis=1)
    return markers,[sw,ne]

def get_cluster_api(lat,lon,nday,nmin,nmax):
    headers = {
            'Content-Type': 'application/json',
            'Cookie': request.headers.get('Cookie')
        }
    params = {
            'n_clusters':nday,
            'nmin':nmin,
            'nmax':nmax,
            'lon':','.join(lon),
            'lat':','.join(lat)
        }
    url = "{url}/api/".format(url=URL_clustering_api)
    response = requests.get(url,params=params, headers=headers)
    print(response.request.url)
    #print(response.json())
    return response.json()



def get_cluster(x,n):
    # torch-kmeans
    #X = torch.tensor(x).unsqueeze(0)
    #model = KMeans(n_clusters=n)
    #result = model(X.to(torch.float32))
    #labels = result.labels.numpy().squeeze()
    #return labels
    return None

def kmeans_plan_otm(pois, npois=20, ndays=5, nmin=3, nmax=6):
    pois = pois.drop_duplicates(subset=['properties.wikidata'])
    df = pois.sort_values(by=["properties.rate", "properties.dist"], ascending=[False, True])
    df = df.iloc[:npois]
    
    df2 = df[["properties.name", "properties.wikidata"]]
    df2["lat"] = df["geometry.coordinates"].apply(lambda x: float(x.split(',')[1][1:-1]))
    df2["lon"] = df["geometry.coordinates"].apply(lambda x: float(x.split(',')[0][1:]))
    df2["kinds"] = df["properties.kinds"]
    
    #df2["lat"] = df["geometry.coordinates"].apply(lambda x: float(x[1]))
    #df2["lon"] = df["geometry.coordinates"].apply(lambda x: float(x[0]))

    x = df2[["lat","lon"]].to_numpy()
    #print(x.shape)
    labels=get_cluster_api(df2["lat"].astype(str).to_list(),df2["lon"].astype(str).to_list(),ndays,nmin,nmax)
    print("result:", labels)
    clusters = get_cluster_api(df2["lat"].astype(str).to_list(),df2["lon"].astype(str).to_list(),ndays,nmin,nmax)
    df2["cluster"]=clusters["clusters"]
    #df2["cluster"]=get_cluster_api(df2["lat"].to_numpy(),df2["lon"].to_numpy())
    #df2["cluster"]=get_cluster(x,ndays)

    cards = []
    for i in range(ndays):
        df_day = df2[df2.cluster == i]
        print(df_day)
        map_day = day_map_otm(df_day)#  dl.Map(children=[dl.TileLayer()]) 
        day_card = [
            html.H4(f"Day {i+1}", className="card-title"),
            html.P("Here is your plan for today", className="card-text",),
            html.Div(children=map_day, style={"height": "300px",'margin-bottom':'20px'})
        ]
        day_card.extend(
            html.P(
                children=f"{k}. {poi['properties.name']}",
                className="card-text",
            )
            for k, (j, poi) in enumerate(df_day.iterrows(), start=1)
        )
        card = dbc.Card([dbc.CardBody(day_card), ],style={'margin-bottom':'20px'})
        cards.append(card)
    return cards

def kmeans_plan_dt(pois, npois=20, ndays=5, nmin=3, nmax=6):
    #df = pois.sort_values(by=["properties.rate", "properties.dist"], ascending=[False, True])
    #df = df.iloc[:npois]
    df= pois.sample(n=20,random_state=42)
    
    df2 = df[["label"]]
    df2["lat"] = df["location.coordinates"].apply(lambda x: float(x.split(',')[1][1:-1]))
    df2["lon"] = df["location.coordinates"].apply(lambda x: float(x.split(',')[0][1:]))
    df2["type"] = df["type"].apply(lambda x: str_to_list(x))
    df2["descriptionEN"]=df["descriptionEN"]
    
    #df2["lat"] = df["geometry.coordinates"].apply(lambda x: float(x[1]))
    #df2["lon"] = df["geometry.coordinates"].apply(lambda x: float(x[0]))

    x = df2[["lat","lon"]].to_numpy()
    print(x.shape)
    labels=get_cluster_api(df2["lat"].astype(str).to_list(),df2["lon"].astype(str).to_list(),ndays,nmin,nmax)
    print("result:", labels)
    clusters = get_cluster_api(df2["lat"].astype(str).to_list(),df2["lon"].astype(str).to_list(),ndays,nmin,nmax)
    df2["cluster"]=clusters["clusters"]
    #df2["cluster"]=get_cluster(x,ndays)

    cards = []
    for i in range(ndays):
        df_day = df2[df2.cluster == i]
        print(df_day)
        map_day = day_map_dt(df_day)#  dl.Map(children=[dl.TileLayer()]) 
        day_card = [
            html.H4(f"Day {i+1}", className="card-title"),
            html.P("Here is your plan for today", className="card-text",),
            html.Div(children=map_day, style={"height": "300px",'margin-bottom':'20px'})
        ]
        day_card.extend(
            html.P(
                children=f"{k}. {poi['label']}",
                className="card-text",
            )
            for k, (j, poi) in enumerate(df_day.iterrows(), start=1)
        )
        card = dbc.Card([dbc.CardBody(day_card), ],style={'margin-bottom':'20px'})
        cards.append(card)
    return cards

def day_map_dt(df_day):
    for i, poi in df_day.iterrows():
        print(poi["type"])
    markers = [
        dl.Marker(
            position=[float(poi.lat), float(poi.lon)],
            icon=poi_icon_dt(poi),
            children=[dl.Tooltip(poi["label"]), dl.Popup(poi["label"])],
        )
        for i, poi in df_day.iterrows()
    ]
    ne = np.max([df_day.lat, df_day.lon], axis=1)
    sw = np.min([df_day.lat, df_day.lon], axis=1)
    return dl.Map(children=[dl.TileLayer(), dl.LayerGroup(markers)], bounds=[sw, ne])

def day_map_otm(df_day):
    markers = [
        dl.Marker(
            position=[float(poi.lat), float(poi.lon)],
            icon=poi_icon_otm(poi["kinds"]),
            children=[dl.Tooltip(poi["properties.name"]), dl.Popup(poi["properties.name"])],
        )
        for i, poi in df_day.iterrows()
    ]
    ne = np.max([df_day.lat, df_day.lon], axis=1)
    sw = np.min([df_day.lat, df_day.lon], axis=1)
    return dl.Map(children=[dl.TileLayer(), dl.LayerGroup(markers)], bounds=[sw, ne])

def query_datatourisme_planner(lat,lon,kinds,limit=300,radius=50):
    headers = {
            'Content-Type': 'application/json',
            'Cookie': request.headers.get('Cookie')
        }
    url = "{url}/api/poi?".format(url=URL_datatourisme)
    params = {
        "longitude":lon,
        "latitude":lat,
        "kinds":json.dumps(kinds,ensure_ascii=False),
        "limit":limit,
        "radius":radius
    }
    response = requests.get(url, params=params, headers=headers)
    print(response.request.url)
    return response.json()

def pois_to_dict(pois):
    features= [
        {
            'id':poi["_id"],
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [float(poi["location"]["coordinates"][0]),float(poi["location"]["coordinates"][1])]},
            'tooltip':poi["label"],
            'popup':poi["descriptionEN"]
        } for poi in pois
    ]
    return {
        'type': 'FeatureCollection',
        'version': 'draft',
        'features': features,
    }
    
def query_opentripmap_planner(lat, lon, kinds):
    itineraire_vacance_key = '5ae2e3f221c38a28845f05b632ea7c5f89c49a5ff84a17768ce137c1'
    headers = {'accept': 'application/geojson'}
    if kinds:
        params = {
            'radius': '50000',
            'lon': str(lat),
            'lat': str(lon),
            'rate': '2',
            'format': 'geojson',
            'kinds': ','.join(kinds),
            'apikey': itineraire_vacance_key,
        }
    else:
        params = {
            'radius': '50000',
            'lon': str(lat),
            'lat': str(lon),
            'rate': '2',
            'format': 'geojson',
            'apikey': itineraire_vacance_key,
        }
    response = requests.get('https://api.opentripmap.com/0.1/en/places/radius', params=params, headers=headers)
    print(response.request.url)
    #print(response.json())
    #df = pd.json_normalize(response.json(), record_path=['features'])
    #df.to_csv("request_otm.csv")
    return response.json()

def add_poi_to_cart(point, store):
    if point is not None:
        if store is None:
            store = []
        store.append(point)
        return store
    
def cart_drop(cart):
    if cart is None:
        raise PreventUpdate

    index = ctx.triggered_id.index
    move_to_index = ctx.triggered[0]["value"]

    if cart is not None:
        # Change position of this element in the carts
        cart_np_array = np.array(cart)

        value = cart_np_array[index]

        cart_np_array = np.delete(cart_np_array, index)
        cart_np_array = np.insert(cart_np_array, move_to_index, value)

        return cart_np_array
    
def cart_rating(cart):
    if cart is None:
        raise PreventUpdate

    index = ctx.triggered_id.index
    rating = ctx.triggered[0]["value"]

    if cart is not None:
        for i, item in enumerate(cart):
            if index == i:
                newItem = item
                newItem["rating"] = rating

                cart[i] = newItem

        return cart
    
def query_save_cart_planner(datas):
    headers = {
            'Content-Type': 'application/json',
            'Cookie': request.headers.get('Cookie')
        }
    url = "{url}/api/poi/history".format(url=URL_datatourisme)
    data = {
        "pois": datas
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.request.url)
    return response.json()

def query_history():
    headers = {
            'Content-Type': 'application/json',
            'Cookie': request.headers.get('Cookie')
        }
    url = "{url}/api/poi/history".format(url=URL_datatourisme)
    response = requests.get(url, headers=headers)

    return response.json()