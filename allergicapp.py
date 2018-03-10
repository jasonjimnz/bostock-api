from flask import Flask, jsonify, request
from neo4j.v1 import GraphDatabase, basic_auth
from model import GraphModel


app = Flask(__name__)


def graph_model(host, port, user, auth):
    graph = GraphDatabase.driver(
        'bolt://{0}:{1}'.format(host, str(port)),
        auth=basic_auth(user,auth)
    )
    session = graph.session()
    return session, graph


host = "localhost"
port = "7687"
user = "neo4j"
auth = "neo4j" # CHANGE TO YOUR NEO$J USER
session, graph = graph_model(host, port, user, auth)
g = GraphModel(session, graph)


@app.route('/', methods=['GET', 'OPTIONS'])
def hello_world():
    print("Hola")
    return jsonify({'msj': 'Hello world'})


@app.route('/register', methods=['POST'])
def register():
    form = request.form
    g.create_user(**{
        'username': form['username'],
        'password': form['password'],
        'first_name': form['first_name'] if 'first_name' in form else None,
        'last_name': form['last_name'] if 'last_name' in form else None,
        'email': form['email']
    })
    res = {'msj': 'Registrado'}
    return jsonify(res), 201


@app.route('/login', methods=['POST'])
def login():
    form = request.form
    login = g.login(form['username'], form['password'])
    return jsonify(login), 200 if login['status'] else 401


@app.route('/allergy/list', methods=['GET'])
def get_alleries():
    return jsonify({'allergies':[x['name'] for x in g.run_query(g.get_formated_query('list_allergies'))]}), 200


@app.route('/search/locations', methods=['POST'])
def search_locations():
    lat = request.form['lat']
    lon = request.form['lon']
    username = request.form['user']
    query = "MATCH (u:User)-[]-(a:Allergy) where u.username = \"%s\" return count(a) as intolerances" % username
    intolerances = [x for x in g.run_query(query)][0]['intolerances']
    results = [{
        'name': x['name'].capitalize(),
        'latitude': x['latitude'],
        'longitude': x['longitude'],
        'total_intolerance': 100 * x['total_intolerance']/intolerances,
        'distance':x['point_distance']
    } for x in g.run_query(
        g.get_formated_query('list_places_by', False) % (username, str(lat), str(lon)))
    ]
    return jsonify({"results": results}), 200

@app.route('/search/locations/unsigned', methods=['POST'])
def search_locations_unsiguned():
    lat = request.form['lat']
    lon = request.form['lon']
    username = request.form['user']
    query = "MATCH (u:User)-[]-(a:Allergy) where u.username = \"%s\" return count(a) as intolerances" % username
    #intolerances = [x for x in g.run_query(query)][0]['intolerances']
    results = [{
        'name': x['name'].capitalize(),
        'latitude': x['latitude'],
        'longitude': x['longitude'],
        'total_intolerance': 200,
        'distance':x['point_distance']
    } for x in g.run_query(
        g.get_formated_query('list_all_places', False) % (str(lat), str(lon)))
    ]
    return jsonify({"results": results}), 200
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
