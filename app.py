import webbrowser
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import webbrowser, os
import requests
import time
import csv






def recuperation_donnees():
    url = 'https://data.anfr.fr/api/records/2.0/downloadfile/format=csv&refine.generation=5G&refine.statut=Techniquement+op%C3%A9rationnel&resource_id=88ef0887-6b0f-4d3f-8545-6d64c8f597da&use_labels_for_header=true'
    response = requests.get(url)
    rows = response.content.decode('utf-8').split("\n")
#Récupération du fichier et écriture du fichier en local
    with open('data.csv', 'w') as f:
        writer = csv.writer(f, delimiter=";")
        for row in rows:
            b = writer.writerow(row.split(';'))



def traitement():
#Traitement du dataframe
    df = pd.read_csv('data.csv',';')
    df['coordonnees'].replace({'\"':""}, regex=True, inplace=True)
    df[['lat','long']] = df['coordonnees'].str.split(',', 1, expand=True)
    df.drop(columns=['coord', 'statut', 'coordonnees'], inplace=True)
    return df


def carte():
#Création de la carte centrée sur Paris
    carte = folium.Map(location=[48.866667,2.333333], zoom_start=13, tiles='cartodbpositron', max_zoom=20)
    df= traitement()

#Création des groupes
    SFR = folium.FeatureGroup(name='SFR')
    BOUYGUES = folium.FeatureGroup(name='BOUYGUES')
    ORANGE = folium.FeatureGroup(name='ORANGE')
    marker_cluster = MarkerCluster(control=False).add_to(carte)

#Itération pour placer les markers
    for i in df.itertuples():
        coords = i[20], i[21]
        
        if i[2] == 'SFR':
            marker = folium.Marker(location=coords, icon = folium.Icon(color='red'))
            marker.add_to(SFR).add_to(marker_cluster)
        elif i[2] == 'BOUYGUES TELECOM':
            marker = folium.Marker(location=coords, icon = folium.Icon(color = 'blue'))
            marker.add_to(BOUYGUES).add_to(marker_cluster)
        elif i[2] == 'ORANGE':
            marker = folium.Marker(location=coords, icon = folium.Icon( color = 'orange'))
            marker.add_to(ORANGE).add_to(marker_cluster)
    SFR.add_to(carte)
    ORANGE.add_to(carte)
    BOUYGUES.add_to(carte)
    
    

#Ajout du panneau de contrôle en le laissant visible
    folium.LayerControl(collapsed=False).add_to(carte)

#Enregistrement de la carte au format html
    carte.save('carte.html')
    return carte

def affichage():
#ouverture de la carte sur le navigateur par défaut
    webbrowser.open('file://' + os.path.realpath('carte.html'))



'''Afin d'éviter de relancer toute la procédure et de gagner du temps on compare la date de dernière modification du fichier .csv.
si elle est inférieure à 7 jours on affiche la carte sinon on relance le téléchargement du fichier'''

if (time.time() - os.path.getmtime('data.csv')) < 604800:
    affichage()
else:
    recuperation_donnees()
    carte()
    affichage()