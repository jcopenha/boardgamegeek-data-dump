import json
import sys
import unicodecsv as csv
import os
from sets import Set
 
def try_parse_int(s, base=10, val=None):
  try:
    return int(s, base)
  except ValueError:
    return val

path_to_json = 'BoardGameGeek.json/201508/boardgame_batches'
print os.listdir(os.path.join(os.curdir,path_to_json))
json_files = [pos_json for pos_json in os.listdir(os.path.join(os.curdir,path_to_json)) if pos_json.endswith('.json')]



# TODO: fix image links
# TODO: num_players junk

headers = Set([])
rows = []
for filename in json_files:
  print filename
  # build headers
  f = open(os.path.join(os.curdir,path_to_json,filename))
  l = f.readline()
  while l:
    j = json.loads(l)
    current = {}
    for k in j.keys():
      if type(j[k]) is dict:
        # flatten language_depenence everything should be 1-5
        diff = 0
        if k == "language_dependence" and len(j[k].keys()) > 0:
          diff = min([int(n) for n in j[k].keys()])-1
        for x in j[k].keys():
          y = x
          if k == "language_dependence":
            x = str(int(x) - diff)
          s = k + "_" + x
          if s in ["ranks_boardgame","ranks_strategygames","ranks_thematic","ranks_familygames","rank_cgs","ranks_abstracts"]:
            headers.add(s)
            current[s] = try_parse_int(j[k][x][1], val = 0)
          else:
            headers.add(s)
            current[s] = j[k][y]
  #        print s
      else:
        if k in ["publisher","designer","family","category","artist","version","subdomain"] and type(j[k]) is list:
          # pick the first name
          headers.add(k)
          if len(j[k]) > 0 :
            current[k] = j[k][0][0]
        elif k in ["name"] and len(j[k]) > 0:
          headers.add(k)
          current[k] = j[k][0]
        elif k in ["honor","mechanic"]:
          headers.add(k)
          current[k] = len(j[k])
        else:
          headers.add(k)
          current[k] = j[k]
  #      print k
  
    l = f.readline()
    rows.append(current)
#    print "finished", current["objectid"]

headers.remove("comments")
headers.remove("py/object")
headers.remove("description")
headers.remove("podcastepisode")
headerList = list(headers)
headerList.sort()
print headerList
#print rows
#for k in rows[0].keys():
#  print k, rows[0][k]

with open('bgg.csv', 'w') as csvfile:
   writer = csv.DictWriter(csvfile, fieldnames=headerList, extrasaction='ignore')
   writer.writeheader()
   for r in rows:
     writer.writerow(r)

# comments data is limited to 100 so skip that
#print len(j["comments"])
