# API Request Dispatch Layer
# Flask microframework driven RESTful API Dispatcher

import json
import operator
import requests
import unidecode
from flask import Flask, request, Response
app = Flask(__name__)


# Home 
@app.route("/")
def index():
  return "PaleoAPI"

@app.route("/occurrence_dups", methods=['GET'])
def occurrence_dups():
 
  
  dist_round = unidecode.unidecode( request.args.get('dist_round') )
  if dist_round is None:
    dist_round = 2

  #occs = requests.get("http://training.paleobiodb.org/comp1.0/occs/list.json?base_name=Canis&show=loc&vocab=pbdb")
  #if 200 == occs.status_code:
  #occs_json = json.loads(occs.content)

  # Loading file since Composite API is timing out on Neotoma API call periodically
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
    lat_rnd = round(occ['lat'], int(dist_round))
    lng_rnd = round(occ['lng'], int(dist_round))

    if 'Neotoma' == occ['database']:
      neotoma.append({"id": occ['occurrence_no'], 
                    "database": occ['database'],
                    "accepted_name": occ['accepted_name'],
                    "lat": lat_rnd, 
                    "lng": lng_rnd, 
                    "min_age": occ['min_age'], 
                    "max_age": occ['max_age'], 
                    "age_unit": occ['age_unit']})

    if 'PaleoBioDB' == occ['database']:
      pbdb.append({"id": occ['occurrence_no'], 
                    "database": occ['database'],
                    "accepted_name": occ['accepted_name'],
                    "lat": lat_rnd, 
                    "lng": lng_rnd, 
                    "min_age": occ['min_age'], 
                    "max_age": occ['max_age'], 
                    "age_unit": occ['age_unit']})

    matches = []
    for pb in pbdb:
      for neo in neotoma: 

        # Coords Match
        if pb['lat'] == neo['lat'] and pb['lng'] == neo['lng']:

          # Time Ranges 
          if neo['max_age'] <= pb['max_age'] and neo['min_age'] >= pb['min_age']:

            # Accepted Names Match
            #if pb['accepted_name'] == neo['accepted_name']:
  
            print "match found"
            matches.append({"pbdb": pb, "neotoma": neo})

  resp = {"status": "shaky at best", "matches": matches}
  return Response(response=json.dumps(resp), status=200, mimetype="application/json") 

@app.errorhandler(404)
def page_not_found(e):
  return "404 - Nope"

if __name__ == '__main__':
  app.run( debug = True )
