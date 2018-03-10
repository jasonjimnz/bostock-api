#-*- coding: utf-8 -*-
import json
from uuid import uuid4
import utm
from openpyxl import load_workbook
import random


class GraphModel(object):
    session = None
    driver = None

    def __init__(self, session, driver):
        self.driver = driver
        self.session = session

    def translate_coords(self, x, y):
        latlon = utm.to_latlon(x, y, 30, 'U')
        return latlon[0], latlon[1]

    def get_formated_query(self, type_of, key_params=True, **kwargs):
        query_dict = {
            'create_user': 'CREATE (u:User{%s})',
            'create_location': 'CREATE (l:Location{%s})',
            'create_allergies': 'CREATE (a:Allergy{%s})',
            'list_allergies': 'MATCH (a:Allergy) %s RETURN a.name AS name',
            'list_places_by': """
                MATCH 
                (l:Location)-[r]-(:Allergy)
                <-[r1:HAS_INTOLERANCE]-(u:User{username:"%s"})  
                RETURN
                 distinct l.rotulo as name,
                 l.lat as latitude, l.lon as longitude,
                 count(r1) as total_intolerance ,
                distance(
                    point({latitude: l.lat, longitude:l.lon}), 
                    point({latitude: %s, longitude: %s})
                ) as point_distance
                ORDER BY point_distance LIMIT 20
            """,
            'list_all_places':"""
                MATCH 
                (l:Location)  
                RETURN
                 distinct l.rotulo as name,
                 l.lat as latitude, l.lon as longitude,
                distance(
                    point({latitude: l.lat, longitude:l.lon}), 
                    point({latitude: %s, longitude: %s})
                ) as point_distance
                ORDER BY point_distance LIMIT 30
            """
        }
        if key_params:
            query_params = ""

            for k in kwargs:
                if kwargs[k]:
                    if query_params != '' and not query_params.endswith(', '):
                        query_params += ", "
                    if type(kwargs[k]) == int:
                        query_params += '{0}:{1}'.format(k, str(kwargs[k]))
                    if type(kwargs[k]) == float:
                        query_params += '{0}:{1}'.format(k, str(kwargs[k]))
                    elif type(kwargs[k]) == str:
                        query_params += '{0}:"{1}"'.format(k, kwargs[k].strip())
            print(query_params)
            return query_dict[type_of] % query_params
        else:
            return query_dict[type_of]

    def run_query(self, query):
        return self.session.run(query)

    def create_user(self, **kwargs):
        query = self.get_formated_query("create_user", **kwargs)
        return self.run_query(query)

    def create_place(self, **kwargs):
        query = self.get_formated_query("create_location", **kwargs)
        return self.run_query(query)

    def create_allergy(self, **kwargs):
        query = self.get_formated_query("create_allergies", **kwargs)
        return self.run_query(query)

    def login(self, user, auth):
        query = 'MATCH (n:User) WHERE n.username = "%s" RETURN count(n) AS exists' % user
        exists = self.session.run(query)
        exists = [x for x in exists.records()][0]['exists']
        if exists > 0:
            query = "MATCH (n:User) WHERE n.username = \"%s\" AND n.password = \"%s\" RETURN count(n) AS logged" % (user, auth)
            login_ok = self.session.run(query)
            login_ok = [x for x in login_ok.records()][0]['logged']
            if login_ok == 1:
                query = """
                MATCH (n:User) 
                WHERE n.username = \"%s\" 
                CREATE (s:UserSession{token:\"%s\"}) 
                MERGE (n)-[:SESSION_OF]->(s)
                RETURN n.username as username, s.token as token
                """ % (user, uuid4().hex)
                print(query)
                user_token = self.session.run(query)
                user_token = [x for x in user_token.records()][0]
                return {'username': user_token['username'], 'token':user_token['token'], 'status': True}
        return {'username': None, 'token': None, 'status': False}


    def load_places_to(self):
        wb = load_workbook('open_data_locales.xlsx')
        rows = [a for a in wb.active.rows]
        json_list = []
        for x, row in enumerate(rows[:100]):
            json_list.append({
                'pos_x': row[8].value,
                'pos_y': row[9].value,
                'rotulo': row[39].value,
                'desc_vial_edificio': row[16].value,
                'num_edificio': row[20].value
            })

        o = open('locales.json', 'w')
        o.write(json.dumps(json_list, ensure_ascii=False))
        o.close()

    def load_places_from_json(self):
        json_dict = json.load(open('locales.json'))
        for l in json_dict:
            query = l
            if query['pos_x'] and query['pos_y']:
                lat, lon = self.translate_coords(
                    float(query['pos_x']),float(query['pos_y'])
                )
            else:
                lat = None
                lon = None
            query['lat'] = lat
            query['lon'] = lon
            self.create_place(**query)

    def load_allergies_from_json(self):
        json_dict = json.load(open('alergias.json'))
        for a in json_dict['allergies']:
            self.create_allergy(name=a)

    def generate_random_relationships(self):
        q = """
        MATCH (a:Location) return id(a) as id
        """
        json_dict = json.load(open('alergias.json'))['allergies']
        query = self.run_query(q)
        query_results = [x for x in query.records()]
        for q1 in query_results:
            a_id = q1['id']
            for x in range(3):
                query_relationship = """
                MATCH (n1:Allergy), (l1:Location) 
                WHERE id(l1) = %s AND n1.name = "%s"
                MERGE (n1)-[:HAS_PRODUCTS_RELATED_WITH_ALLERGY]->(l1)
                """ % (int(a_id), json_dict[random.randint(0,len(json_dict)-1)])
                self.run_query(query_relationship)
        return True
