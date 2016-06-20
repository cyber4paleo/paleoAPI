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

  pbdb = []
  neotoma = []
  compact = []
  for occ in occs_json['records']:

    # Normalize to Ma
    if "ybp" == occ['age_unit']:

      min_age_tmp = ( float(occ['min_age']) / 1000000 )
      max_age_tmp = ( float(occ['max_age']) / 1000000 )

      occ['age_unit'] = 'Ma'
      occ['min_age'] = min_age_tmp
      occ['max_age'] = max_age_tmp

    # Normalize lat/lng to XX.XX level of precision
    lat_rnd = round(occ['lat'], 2)
    lng_rnd = round(occ['lng'], 2)

    if 'Neotoma' == occ['database']:
      neotoma.append({"id": occ['occurrence_no'], 
                    "database": occ['database'],
                    "lat": lat_rnd, 
                    "lng": lng_rnd, 
                    "min_age": occ['min_age'], 
                    "max_age": occ['max_age'], 
                    "age_unit": occ['age_unit']})

    if 'PaleoBioDB' == occ['database']:
      pbdb.append({"id": occ['occurrence_no'], 
                    "database": occ['database'],
                    "lat": lat_rnd, 
                    "lng": lng_rnd, 
                    "min_age": occ['min_age'], 
                    "max_age": occ['max_age'], 
                    "age_unit": occ['age_unit']})

    matches = []
    for pb in pbdb:
      for neo in neotoma: 

        if pb['lat'] == neo['lat'] and pb['lng'] == neo['lng']:
          print "match found"
          matches.append({"pbdb": pb, "neotoma": neo})



    #sorted_pbdb    = sorted(pbdb, key=operator.itemgetter('lat'))
    #sorted_neotoma = sorted(neotoma, key=operator.itemgetter('lat'))




    resp = {"status": "shaky at best", "matches": matches}

  return Response(response=json.dumps(resp), status=200, mimetype="application/json") 

@app.errorhandler(404)
def page_not_found(e):
  return "404 - Nope"

if __name__ == '__main__':
  app.run( debug = True )
