import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import calendar
import os
# creation du dossier pour les graphiques
os.makedirs("graphiques", exist_ok=True)
# chargement du csv
df = pd.read_csv("visionnage_series.csv")


#partie 1: preparation & nettoyage des donnees
# a_ convertir les colonnes date et heure_debut en objet datetime
df["date"]=pd.to_datetime(df["date"], format= "%Y-%m-%d")
df["heure_debut"]=pd.to_datetime(df["heure_debut"], format = "%H:%M").dt.time
# b_ extraire le jour de la semaine dans une nouvelle colonne jour _semaine
df["jour_semaine"]=df["date"].dt.day_name()
# c_ ajoute l'heure_arrondie
df["heure_arrondie"]=df["heure_debut"].apply(lambda x:x . hour)
# d_detection et gestion des valeurs manquantes
print(df.isnull().sum())
df=df.dropna()
# e_ verification et supprition des doublons
print(f"les doublons: {df.duplicated().sum()}")
df= df.drop_duplicates()


#partie 2: analyse temporelle
# a_ repartition des sessions par heure de la journee (courbe)
plt.figure(figsize=(15, 7))
df['heure_arrondie'].value_counts().sort_index().plot(kind='line', marker='o')
plt.title("Fréquence des heures de visionnage")
plt.xlabel("Heure")
plt.ylabel("Sessions")
plt.savefig("graphiques/frequence_heures.png")
plt.show()
plt.close()
# b_ repartition par jour de la semaine
order_jours=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
#Barres groupées
plt.figure(figsize=(15,7))
sns.countplot(x="jour_semaine", data=df, order=order_jours, color="steelblue")
plt.title("repartitionde session par jour de la semaine")
plt.xlabel("jour de la semaine")
plt.ylabel("sessions")
plt.savefig("graphiques/repartition_jours.png")
plt.show()
plt.close()
# c_ realisation d'une heatmap jour/heure
heatmap_data=df.pivot_table(index="jour_semaine", columns="heure_arrondie", values="durée", aggfunc="count", fill_value=0)
heatmap_data=heatmap_data.reindex(order_jours)
plt.figure(figsize=(18,10))
sns.heatmap(data= heatmap_data, cmap="coolwarm",annot=True)
plt.title("heatmap jour & heure")
plt.xlabel("heure de la journee")
plt.ylabel("jour de la semaine")
plt.savefig("graphiques/heatmap_jour_heure.png")
plt.show()
plt.close()

#partie 3: analyse qualitative
# a_ identification de la serie la plus regardee sur chaque plateforme
top_series=df.groupby(["plateforme","série"]).size().reset_index(name="count")
top_serie= top_series.loc[top_series.groupby("plateforme")["count"].idxmax()]
#diagrammme en barres
plt.figure(figsize=(15,7))
sns.barplot(x="plateforme",y="count",hue="série",data=top_serie)
plt.title("serie la plus regardees par plateforme")
plt.ylabel("visionnages")
plt.savefig("graphiques/top_series_plateforme.png")
plt.show()
plt.close()
# b_ identificationdu genre dominant par plateform
top_genres=df.groupby(["plateforme","genre"]).size().reset_index(name="count")
top_genres=top_genres.loc[top_genres.groupby("plateforme")["count"].idxmax()]
#diagramme cerculaire
for plateforme in df ["plateforme"].unique():
    plt.figure(figsize=(12,6))
    df[df["plateforme"]==plateforme]["genre"].value_counts().plot.pie(autopct="%1.1f%%")
    plt.title(f"repartition des genres sur {plateforme}")
    plt.savefig(f"graphiques/repartition_genres_{plateforme.lower().replace(' ','_')}.png")
    plt.show()
    plt.close()
# c_ comparaison des duree moyenne de session selon genre
#calcule duree moyenne de session par genre
duree_genre= df.groupby("genre")["durée"].mean().reset_index().sort_values("durée", ascending=False)
# (histogramme)
plt.figure(figsize=(12, 6))
df.groupby('plateforme')['durée'].mean().plot(
    kind='bar',
    color=['#e41a1c', '#377eb8', '#4daf4a']  # rouge, bleu, vert
)
plt.title("Durée moyenne par plateforme")
plt.xlabel("Plateforme")
plt.ylabel("Minutes moyennes")
plt.savefig("graphiques/duree_moyenne.png")
plt.show()
plt.close()


# Partie 4: Comparaison Inter-plateformes
# a_ Temps moyen de visionnage le soir (entre 18h et 00h)
soir = df[(df["heure_arrondie"] >= 18) & (df["heure_arrondie"] <= 23)]
duree_soir = soir.groupby("plateforme")["durée"].mean().reset_index()
# Visualisation
plt.figure(figsize=(10, 6))
sns.barplot(x="plateforme", y="durée", data=duree_soir, color="#4e79a7")
plt.title("Durée moyenne des sessions du soir par plateforme")
plt.ylabel("Durée moyenne (min)")
plt.xlabel("Plateforme")
plt.savefig("graphiques/duree_moyenne_soir.png")
plt.show()
plt.close()

# b_ Nombre de sessions longues (>60 min)
sessions_longues = df[df["durée"] > 60]
count_longues = sessions_longues["plateforme"].value_counts().reset_index()
count_longues.columns = ["plateforme", "count"]
# Visualisation
plt.figure(figsize=(10, 6))
sns.barplot(x="plateforme", y="count", data=count_longues, color="steelblue")
plt.title("Nombre de sessions longues par plateforme")
plt.ylabel("Nombre de sessions")
plt.xlabel("Plateforme")
plt.savefig("graphiques/sessions_longues.png")
plt.show()
plt.close()

# c_ Comparaison de comportement de visionnage (semaine vs week-end)
df["type_jour"] = df["jour_semaine"].apply(lambda x: "week-end" if x in ["Saturday", "Sunday"] else "semaine")
sessions_type_jour = df.groupby(["plateforme", "type_jour"]).size().reset_index(name="count")
# Visualisation (Barres groupées)
plt.figure(figsize=(15, 8))
sns.barplot(x="plateforme", y="count", hue="type_jour", data=sessions_type_jour)
plt.title("Répartition des sessions entre semaine et week-end par plateforme")
plt.ylabel("Nombre de sessions")
plt.xlabel("Plateforme")
plt.savefig("graphiques/sessions_semaine_weekend.png")
plt.show()
plt.close()

# Ajout: Durée totale par plateforme (Diagramme en barres)
duree_totale = df.groupby("plateforme")["durée"].sum().reset_index()
plt.figure(figsize=(10, 6))
sns.barplot(x="plateforme", y="durée", data=duree_totale, color="teal")
plt.title("Durée totale par plateforme")
plt.ylabel("Durée totale (min)")
plt.xlabel("Plateforme")
plt.savefig("graphiques/duree_totale_plateforme.png")
plt.show()
plt.close()


# Partie 5: Export et Synthèse
# Créer un fichier CSV avec les principaux résultats
platforms = df['plateforme'].unique()
resultats = pd.DataFrame({
    'Plateforme': platforms,
    'Série_plus_regardée': [top_serie[top_serie['plateforme'] == p]['série'].values[0] for p in platforms],
    'Genre_dominant': [top_genres[top_genres['plateforme'] == p]['genre'].values[0] for p in platforms],
    'Duree_moyenne_soir': [duree_soir[duree_soir['plateforme'] == p]['durée'].values[0] for p in platforms],
    'Sessions_longues': [count_longues[count_longues['plateforme'] == p]['count'].values[0] for p in platforms]
})
# Sauvegarder les résultats principaux dans resultats_analyse.csv
resultats.to_csv('resultats_analyse.csv', index=False)