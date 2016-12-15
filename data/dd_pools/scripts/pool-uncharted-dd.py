#!/usr/bin/env python
import json
import argparse

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-d", "--depth", help="Depth to pool to",
                    default=100, type=int)
parser.add_argument("-e", "--extperdoc",
                    help="Pool the first N extracts from a document",
                    default=1, type=int)
parser.add_argument("file", help="JSON file")
args = parser.parse_args()

class JSONSetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)

def prune(lst, tlen=3):
    return sorted([t for t in lst if isinstance(t, list) and len(t) == tlen],
                  key=lambda t: t[tlen-1], reverse=True)

pool = {'Point Fact': {},
        'Cluster Identification': {},
        'Cluster Facet': {},
        'Aggregation': {}}

data = json.loads(open(args.file, "r").read())
for q in data:
    if 'answers' not in q:
        continue
    resp = q['answers']
    qid = q['question_id']
    qtype = q['questionType']

    if qtype not in pool:
        qtype = "Aggregation"
    
    if qid not in pool[qtype]:
        if qtype == 'Cluster Identification':
            pool[qtype][qid] = set()
        else:
            pool[qtype][qid] = {}

    if len(resp) == 0:
        continue

    depth = 0
    
    tlen = 3
    if qtype == 'Cluster Identification':
        tlen = 2
    for a in prune(resp, tlen):
        if qtype == 'Cluster Identification':
            docid, score = a
            extract = "foo"
        else:
            extract, docid, score = a
        if docid in pool[qtype][qid] and len(pool[qtype][qid][docid]) >= args.extperdoc:
            continue
        depth += 1
        if (depth > args.depth):
            break
        if qtype == 'Cluster Identification':
            pool[qtype][qid].add(docid)
        else:
            if docid not in pool[qtype][qid]:
                pool[qtype][qid][docid] = set()
            pool[qtype][qid][docid].add(extract)

for qtype in pool:
    with open("uncharted" + qtype + ".pool", "w") as outfp:
        outfp.write(json.dumps(pool[qtype], cls=JSONSetEncoder))
