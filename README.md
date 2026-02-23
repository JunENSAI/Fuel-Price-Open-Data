# Fuel-Price-Open-Data

Ce projet vise à essayer de pratiquer les données publiques ouvertes sur le prix des carburant en France. L'architecture pensée est  : Postgresql pour le schema relationnel , Python pour la collecte via API et traitement en temps réel. Le but est d'expérimenter l'ingestion des données pour une base pereine et contrôlée.

Les données qui seront traitées proviennent de l'api (ouvert à tous et à toutes) des prix de carburant en France : https://swagger.2aaz.fr/?urls.primaryName=Fuel%20prices%20API%20(prix-carburants)#/ (qui est plutôt une réutilisation mais fonctionnel).

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

