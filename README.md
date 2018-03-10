# Bostock API

Python based API connected with NEO4J as a database engine
for helping people to get relevance between people with allergies
with restaurant dishes (and similar places)

## Requirements
- Python 3.6
- Neo4J 3.3.1
- Python Packages
    - neo4j-driver
    - flask
    - openpyxl (for excel reading)
    - utm (For lat/lon fixing)

## How to install it

- Use NEO4J installed locally or download a Docker
container for using with
```bash
sudo docker run -p 7687:7687 -p 7474:7474 -p 80:808 -d -t -v /PATH_TO_DATABASE_FOLDER/YOUR_DATABASE_FOLDER:/var/lib/neo4j/data/databases/graph.db jasonjimnz/neo4j-community
```

 - Login to [http://localhost:7474](http://localhost:7474) with User: neo4j and Pass: neo4j
 you will have to change the password
 - Once the password is changed in Neo4J the bolt link is bolt://localhost:7687 for
 direct socket connection to NEO4J (faster than API REST)
 - Before running the Flask server, in the allergicapp.py file you will
 have to change the password of the NEO4J user to your own password for
 building the new model
 - Once the NEO4J credentials has been fixed, execute the following code:
 ```python
 from allergicapp import *
 g.load_places_to() # For converting the XLSX file to JSON
 g.load_places_from_json() # For the creation of places from JSON
 g.load_allergies_from_json() # For the creation of allergies JSON
 g.generate_random_relationships() # For the creation of random relationships between Allergies and Locations
 # If you want to get some allergies to your profile you can create a user and then link some Allergies to them
 ```

 - Once the Database is built run the following command
 ```bash
 python3 allergicapp.py
 ```

 - The API will be available on http://localhost:3000

 ## DATASETS

 - [Censo de locales, sus actividades y terrazas de hostelería y restauración](https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=66665cde99be2410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default)
 CSV curated and transformed for adding some entries to the Graph, from the Ayuntamiento de Madrid open data website