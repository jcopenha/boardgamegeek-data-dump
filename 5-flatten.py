import json
import sys
import unicodecsv as csv
import os
from sets import Set
import argparse
 
def try_parse_int(s, base=10, val=None):
  try:
    return int(s, base)
  except ValueError:
    return val

def parse_json_file(filename):
  headers = Set([])
  rows = []
  f = open(filename)
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
  return headers, rows

parser = argparse.ArgumentParser(description='Flatten BoardGameGeek JSON files.')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False, help='Verbose output')

args = parser.parse_args()

headers_to_remove = ["comments","py/object","description","podcastepisode"]

#TODO do some args handling..
path_to_json = 'BoardGameGeek.json/201508/boardgame_batches'
#print os.listdir(os.path.join(os.curdir,path_to_json))
json_files = [pos_json for pos_json in os.listdir(os.path.join(os.curdir,path_to_json)) if pos_json.endswith('.json')]
print ">> Found", len(json_files), "JSON files to parse"



# TODO: fix image links
# TODO: num_players junk

current_file_count = 0
headers = Set([])
rows = []
for filename in json_files:
  if current_file_count % 100 == 0 and args.verbose:
     print "+ Processed", current_file_count, "of", len(json_files)
  h, r = parse_json_file(os.path.join(os.curdir, path_to_json, filename))
  headers = headers.union(h)
  rows = rows + r
  current_file_count += 1
print ">> All files processed"

for h in headers_to_remove:
  headers.remove(h)

header_list = list(headers)
header_list.sort()
if args.verbose:
  print ">> Generating CSV with following headers:"
  for h in header_list:
    print "+", h

print ">> Found", len(rows), "boardgames"
current_boardgame_count = 0
with open('bgg.csv', 'w') as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=header_list, extrasaction='ignore')
  writer.writeheader()
  for r in rows:
    writer.writerow(r)
    current_boardgame_count += 1
    if current_boardgame_count % 1000 == 0 and args.verbose:
      print "+ Written", current_boardgame_count, "boardgames"

print ">> Fisnished writing bgg.csv"
