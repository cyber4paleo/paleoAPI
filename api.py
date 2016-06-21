# API Request Dispatch Layer
# Flask microframework driven RESTful API Dispatcher

import json
import random
import StringIO
import operator
import requests
import collections
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask, request, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
app = Flask(__name__)


# Home 
@app.route("/")
def index():
  return "PaleoAPI"

# Plot
@app.route('/plot.png')
def plot():

 occs = requests.get("http://training.paleobiodb.org/comp1.0/occs/list.json?base_name=cetacea&show=subq,loc&vocab=pbdb", timeout=None)
 if 200 == occs.status_code:
   occs_json = json.loads(occs.content)

   composite_count = len(occs_json['records'])

   # inits
   pbdb    = []
   neotoma = []
   ages    = []

   # Filter List for incomplete records
   occs_json['records'][:] = [occ for occ in occs_json['records'] if 'max_age' in occ]
   for occ in occs_json['records']:

     # Normalize to Ma
     if 'age_unit' in occ and "ybp" == occ['age_unit']:

       min_age_tmp = ( float(occ['min_age']) / 1000000 )
       max_age_tmp = ( float(occ['max_age']) / 1000000 )

       occ['age_unit'] = 'Ma'
       occ['min_age'] = min_age_tmp
       occ['max_age'] = max_age_tmp
       
     if 'min_age' in occ:
       min_age = occ['min_age']

     if 'max_age' in occ:
       max_age = occ['max_age']
    
     # calculate mean
     mean_age = np.mean([max_age, min_age])

     ages.append(mean_age)

     # Splitting out concat'ed data for comparison
     if 'Neotoma' == occ['database'] and mean_age is not None:
       neotoma.append(float(mean_age))

     if 'PaleoBioDB' == occ['database'] and mean_age is not None:
       pbdb.append(float(mean_age))



   # Determine our Age Range
   hi_max = max(occ['max_age'] for occ in occs_json['records'])
   lo_min = min(occ['min_age'] for occ in occs_json['records'])

   # keep track of the breakdown
   pbdb_counts = len(pbdb)
   neo_counts  = len(neotoma)


   pb_points  = np.array( pbdb )
   neo_points = np.array( neotoma )


   bin_size = np.arange(0.0, 0.6, 0.01)

   bin_size = np.arange(0, 5, 0.1)

   fig = plt.gcf()
   #fig = plt.figure()

   pn, pbins, ppatches = plt.hist(pb_points, normed=0, color='green', bins=bin_size, alpha=0.5)
   bn, bbins, bpatches = plt.hist(neo_points, normed=0, color='red', bins=bin_size, alpha=0.5)

   #p, bins, patches = plt.hist([pb_points, neo_points], n_bins, normed=0, color=['green', 'blue'], alpha=0.5)


   #plt.plot(pn)
   #plt.plot(bn)
   #plt.xlim(0, 0.1)
   plt.xlabel('Geologic Time (Ma)')
   plt.ylabel('# Occurrences')
   plt.title('Occurrence Distribution')
   plt.grid(True)

   # Write to canvas for web display
   canvas = FigureCanvas(fig)
   output = StringIO.StringIO()
   canvas.print_png(output)

   return Response(response=output.getvalue(), status=200, mimetype="image/png")
   #return Response(response=json.dumps({'okay':'okay'}), status=200, mimetype="application/json")

# Occurrence Duplication Check
@app.route("/occurrence_dups", methods=['GET'])
def occurrence_dups():
 
  data_source = request.args.get('data_source')
  dist_round  = request.args.get('dist_round')
  base_name   = request.args.get('base_name')

  if dist_round is None:
    dist_round = 2

  # TODO: Neotoma Fix Timeout
  occs_json = []
  if 'api' == data_source:
    occs = requests.get("http://training.paleobiodb.org/comp1.0/occs/list.json?base_name=" + base_name + "&show=subq,loc&vocab=pbdb", timeout=None)
    if 200 == occs.status_code:
      occs_json = json.loads(occs.content)
    
  elif 'file' == data_source: 

    # Loading file since Composite API is timing out on Neotoma API call periodically
    occs_json = json.load(open('./canis.json'))  


  composite_count = len(occs_json['records'])
  print "Number of records: " + str(len(occs_json['records']))

  # inits
  pbdb    = []
  neotoma = []
  compact = []
  matches = []

  # Filter List for incomplete records
  occs_json['records'][:] = [occ for occ in occs_json['records'] if 'max_age' in occ]

  
  for occ in occs_json['records']:

    # Normalize to Ma
    if 'age_unit' in occ and "ybp" == occ['age_unit']:

      min_age_tmp = ( float(occ['min_age']) / 1000000 )
      max_age_tmp = ( float(occ['max_age']) / 1000000 )

      occ['age_unit'] = 'Ma'
      occ['min_age'] = min_age_tmp
      occ['max_age'] = max_age_tmp

    # init
    if 'age_unit' in occ:
      age_unit = occ['age_unit']

    if 'min_age' in occ:
      min_age = occ['min_age']

    if 'max_age' in occ:
      max_age = occ['max_age']
    

    print "orig lat: " + str(occ['lat'])
    print "orig lng: " + str(occ['lng'])    

    # Normalize lat/lng to XX.XX level of precision
    lat_rnd = round(occ['lat'], int(dist_round))
    lng_rnd = round(occ['lng'], int(dist_round))

    # Splitting out concat'ed data for comparison
    if 'Neotoma' == occ['database']:
      neotoma.append({"id": occ['occurrence_no'], 
                    "database": occ['database'],
                    "accepted_name": occ['accepted_name'],
                    "collection_name": occ['collection_name'],
                    "lat": lat_rnd, 
                    "lng": lng_rnd, 
                    "min_age": min_age, 
                    "max_age": max_age, 
                    "age_unit": age_unit})

    if 'PaleoBioDB' == occ['database']:
      pbdb.append({"id": occ['occurrence_no'], 
                    "database": occ['database'],
                    "accepted_name": occ['accepted_name'],
                    "collection_name": occ['collection_name'],
                    "lat": lat_rnd, 
                    "lng": lng_rnd, 
                    "min_age": min_age, 
                    "max_age": max_age, 
                    "age_unit": age_unit})

  # Determine our Age Range
  hi_max = max(occ['max_age'] for occ in occs_json['records'])
  lo_min = min(occ['min_age'] for occ in occs_json['records'])

  # keep track of the breakdown
  pbdb_counts = len(pbdb)
  neo_counts  = len(neotoma)

  print "Starting Matching section"
 
  # If data records match following three criteria, call it a match
  for pb in pbdb:
    for neo in neotoma: 

      # Coords Match
      if 1.0 >= abs(pb['lat'] - neo['lat']) and 1.0 >= abs(pb['lng'] - neo['lng']):

        print "Coords Match"

        # Time Ranges 
        if neo['max_age'] <= pb['max_age'] and neo['min_age'] >= pb['min_age']:

          print "Time match"

          # Accepted Names Match
          if pb['accepted_name'] == neo['accepted_name']:
            print "match found"
            matches.append({"pbdb": pb, "neotoma": neo})

  print "done matching"

  # Build JSON Response
  resp = (("status", "shaky at best"), 
          ("composite_count", composite_count), 
          ("pbdb_count", pbdb_counts), 
          ("neo_count", neo_counts), 
          ("num_matches", len(matches)), 
          ("hi_max", hi_max),
          ("low_min", lo_min),
          ("matches", matches))
  resp = collections.OrderedDict(resp)

  return Response(response=json.dumps(resp), status=200, mimetype="application/json") 

@app.errorhandler(404)
def page_not_found(e):
  return "404 - Nope"

if __name__ == '__main__':
  app.run( debug = True )
