#!/bin/bash

echo " Démarrage de l'import MongoDB..."

mongoimport --db scientifique --collection chercheurs --file /data/chercheurs.json --jsonArray
mongoimport --db scientifique --collection collaborations --file /data/collaborations.json --jsonArray
mongoimport --db scientifique --collection institutions --file /data/institutions.json --jsonArray
mongoimport --db scientifique --collection publications --file /data/publications.json --jsonArray
mongoimport --db scientifique --collection stats_pays --file /data/stats_pays.json --jsonArray

echo "Import terminé !"
