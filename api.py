# API Request Dispatch Layer
# Flask microframework driven RESTful API Dispatcher

import json
import operator
import requests
from flask import Flask, request, Response
app = Flask(__name__)


# Home 
@app.route("/")
def index():
  return "PaleoAPI"

@app.route("/occurrence_dups", methods=['GET'])
def occurrence_dups():
 
  # Loading file since Composite API is timing out on Neotoma API call periodically

  #occs = requests.get("http://training.paleobiodb.org/comp1.0/occs/list.json?base_name=Canis&show=loc&vocab=pbdb")
  #if 200 == occs.status_code:
  #occs_json = json.loads(occs.content)

  occs_json = json.load(open('./canis.json'))  

  compact = []
  for occ in occs_json['records']:
    print occ
    compact.append({"id": occ['occurrence_no'], 
                    "database": occ['database'],
                    "lat": occ['lat'], 
                    "lng": occ['lng'], 
                    "min_age": occ['min_age'], 
                    "max_age": occ['max_age'], 
                    "age_unit": occ['age_unit']})

    sorted_compact = sorted(compact, key=operator.itemgetter('lat'))

  return Response(response=json.dumps(sorted_compact), status=200, mimetype="application/json") 

@app.errorhandler(404)
def page_not_found(e):
  return "404 - Nope"

if __name__ == '__main__':
  app.run( debug = True )
