# Fuel-Price-Open-Data

Ce projet vise à essayer de pratiquer les données publiques ouvertes sur le prix des carburant en France. L'architecture pensée est  : Postgresql pour le schema relationnel , Python pour la collecte via API et traitement en temps réel. Le but est d'expérimenter l'ingestion des données pour une base pereine et contrôlée.

Les données qui seront traitées proviennent de l'api (ouvert à tous et à toutes) des prix de carburant en France : https://swagger.2aaz.fr/?urls.primaryName=Fuel%20prices%20API%20(prix-carburants)#/ (qui est plutôt une réutilisation mais fonctionnel).

## Structure du projet 

```plaintext
projet_open_data/
├── data/                  # Stockage temporaire des données (optionnel)
├── sql/                   # Scripts d'initialisation de la base de données
│   ├── create_dimensions.sql
│   └── create_facts.sql
├── src/                   # Code source Python
│   ├── extract/           # Modules d'appel à l'API
│   ├── transform/         # Nettoyage et formatage des données 
│   ├── load/              # Chargement en base (SQLAlchemy)
│   └── main.py            # Point d'entrée de l'orchestrateur
├── poetry.lock            # Fichier de verrouillage des versions exactes
├── pyproject.toml         # Définition des dépendances du projet
└── README.md              # Documentation du projet
```

## Architecture

### Gestion des packages Python

Pour ne pas s'embêter avec les dépendances entre les librairies python le fichier `poetry.lock` contiendra déjà tous les dépendances nécessaire à ce projet.


### PostgreSQL

La configuration basique prévaut dans PostgreSQL :

- création d'utilisateur et affectation mot de passe :
    ```text
    CREATE USER user_fuel WITH PASSWORD 'open-data@fuel';
    ```
- création base de données pour cet utilisateur :
    ```text
    CREATE DATABASE fuel_db OWNER user_fuel;
    ```
- accorder toutes les privilèges à cet utilisateur sur la base :
    ```text
    GRANT ALL PRIVILEGES ON DATABASE fuel_db TO user_fuel;
    ```

La structure des bases de données qui seront enregistrées dans `fuel_db` suit un **schema étoile** qui visent à separer : les mesures quantitatives (faits) et les axes d'analyse descriptifs (dimensions). Ce modèle optimise les performances de lecture pour les requêtes analytiques (OLAP) au détriment de l'écriture.

Le modèle de données est constitué comme suit :

- **Table de Faits** (`fact_fuel_price`)

    C'est la table centrale qui enregistre l'historique des prix. Elle contient :

    - Les clés étrangères vers les dimensions (`station_id`, `fuel_id`, `date_id`).

    - La mesure : le prix du carburant (`price_value`) à un instant T.

    - L'horodatage de la mise à jour (`update_time`).

- **Tables de Dimensions**

    Elles apportent le contexte aux mesures :

    - `dim_station` : Référentiel des points de vente (ID technique, adresse, ville, code postal, coordonnées GPS). Cette dimension gère l'unicité des stations.

    - `dim_fuel` : Typologie des carburants (Gazole, SP95, E10, etc.).

    - `dim_date` : Calendrier permettant des agrégations temporelles performantes (année, mois, jour, jour de la semaine).
