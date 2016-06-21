import json
import requests
import numpy as np
import matplotlib.pyplot as plt

pbdb = []
neotoma = []
ages = []

occs = requests.get("http://training.paleobiodb.org/comp1.0/occs/list.json?base_name=canidae&show=subq,loc&vocab=pbdb", timeout=None)
if 200 == occs.status_code:
  occs_json = json.loads(occs.content)
  occs_json['records'][:] = [occ for occ in occs_json['records'] if 'max_age' in occ]
  
  for occ in occs_json['records']:
    
    if 'age_unit' in occ and 'ybp' == occ['age_unit']:
      min_age_tmp = ( float(occ['min_age']) / 1000000 )
      max_age_tmp = ( float(occ['max_age']) / 1000000 )

      occ['min_age'] = min_age_tmp
      occ['max_age'] = max_age_tmp

    if 'min_age' in occ:
      min_age = occ['min_age']
 
    if 'max_age' in occ:
      max_age = occ['max_age']

    mean_age = np.mean([max_age, min_age])

    ages.append(mean_age)

    if 'Neotoma' == occ['database'] and mean_age is not None:
      neotoma.append(float(mean_age))

    if 'PaleoBioDB' == occ['database'] and mean_age is not None:
      pbdb.append(float(mean_age))

  hi_max = max(occ['max_age'] for occ in occs_json['records'])
  lo_min = min(occ['min_age'] for occ in occs_json['records'])

  pb_points  = np.array(pbdb)
  neo_points = np.array(neotoma)

  n_bins = 100
  fig = plt.figure()
 
  pb_points = 100 + 15 * np.random.randn(10000)

  pn, pbins, ppatches = plt.hist(pb_points, n_bins, normed=0, color='green', alpha=0.5)
  #bn, bbins, bpatches = plt.hist(neo_points, n_bins, normed=0, color='red', alpha=0.5)

  plt.plot(pn)
  #plt.plot(bn)
  #plt.xlim(lo_min, hi_max)
  plt.xlabel('Geologic Time (Ma)')
  plt.ylabel('# Occurrences')
  plt.title('Occurrence Distribution')
  plt.grid(True)

  plt.show()

