from flask import Flask, jsonify
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import re


app = Flask(__name__, static_url_path="")


@app.route('/google/<query>', methods=['GET'])
def get_query_google(query):
    search_term = str(query)
    url = 'https://www.google.com/complete/search?client=hp&hl=en&sugexp=msedr&gs_rn=62&gs_ri=hp&cp=1&gs_id=9c&q='\
          + search_term + ' vs&xhr=t'
    r = requests.get(url)
    data = r.json()
    values = list(map(lambda x: re.search(r'(?<=<b>)(.*?)(?=</b>)', x[0]).group(0), data[1]))
    return jsonify({search_term: values})


@app.route('/wikidata/<query>', methods=['GET'])
def get_query_wikidata(query):
    search_term = query
    # get the object id from wikidata api
    api_endpoint = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'language': 'en',
        'search': search_term
    }
    r = requests.get(api_endpoint, params=params)
    object_id = r.json()['search'][0]['id']

    # query wikidata for subclass of
    query_string = 'SELECT ?item ?itemLabel WHERE { \
      ?item wdt:P279 wd:' + object_id + '. \
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}'

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(query_string)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    bindings = results['results']['bindings']
    all_values = [n['itemLabel']['value'] for n in bindings]
    values = [n for n in all_values if not n.startswith('Q')]
    return jsonify({search_term: values})


@app.route('/')
def index():
    return "it's working!"


if __name__ == "__main__":
    app.run()

