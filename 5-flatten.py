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

def flatten_simple(key, values):
  value = None
  if key in ["publisher","designer","family","category","artist","version","subdomain"] and type(values[key]) is list:
    # pick the first name
    if len(values[key]) > 0 :
      value = values[key][0][0]
  elif key in ["name"] and len(values[key]) > 0:
    value = values[key][0]
  elif key in ["honor","mechanic"]:
    value = len(values[key])
  else:
    value = values[key]
  
  return key, value

def flatten_dict(key, values):
  value = None
  new_key = None
  headers = Set([])
  flattened = {}
  # flatten language_depenence everything should be 1-5
  diff = 0
  if key == "language_dependence" and len(values[key].keys()) > 0:
    diff = min([int(n) for n in values[key].keys()])-1
  for x in values[key].keys():
    y = x
    if key == "language_dependence":
      x = str(int(x) - diff)
    new_key = key + "_" + x
    if new_key in ["ranks_boardgame","ranks_strategygames","ranks_thematic","ranks_familygames","rank_cgs","ranks_abstracts"]:
      value = try_parse_int(values[key][x][1], val = 0)
    else:
      value = values[key][y]
    
    headers.add(new_key)
    flattened[new_key] = value

  return headers, flattened

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
        h, d = flatten_dict(k,j)
        headers = headers.union(h)
        current.update(d)
      else:
        h, v = flatten_simple(k,j)
        headers.add(h)
        current[h] = v
  
    l = f.readline()
    rows.append(current)
  return headers, rows

def main():
  #TODO: add argparse for path_to_json?
  parser = argparse.ArgumentParser(description='Flatten BoardGameGeek JSON files.')
  parser.add_argument('--verbose', dest='verbose', action='store_true',
                      default=False, help='Verbose output')
  args = parser.parse_args()

  headers_to_remove = ["comments","py/object","description","podcastepisode"]

  path_to_json = 'BoardGameGeek.json/201508/boardgame_batches'
  json_files = [pos_json for pos_json in os.listdir(os.path.join(os.curdir,path_to_json)) if pos_json.endswith('.json')]
  print ">> Found", len(json_files), "JSON files to parse"

  # TODO: fix image links
  # TODO: num_players junk

  current_file_count = 0
  headers = Set([])
  rows = []
  for filename in json_files:
    if args.verbose and current_file_count % 100 == 0:
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
      if args.verbose and current_boardgame_count % 1000 == 0:
        print "+ Written", current_boardgame_count, "boardgames"

  print ">> Fisnished writing bgg.csv"

if __name__ == "__main__":
    main()