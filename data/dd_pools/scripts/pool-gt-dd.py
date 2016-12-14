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
parser.add_argument("-i", "--clusterid",
                    help="Cluster ID mode (tuples of length 2 in answer)",
                    action='store_true')
parser.add_argument("file", help="JSON file")
args = parser.parse_args()

class JSONSetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        else:
            return json.JSONEncoder.default(self, obj)

def prune(lst):
    m = 3
    if args.clusterid:
        m = 2
    return sorted([t for t in lst if len(t) == m],
                  key=lambda t: t[m-1], reverse=True)

pool = {}

data = json.loads(open(args.file, "r").read())
for q in data:
    resp = q['answer']
    qid = q['id']

    if qid not in pool:
        if args.clusterid:
            pool[qid] = set()
        else:
            pool[qid] = {}

    if len(resp) == 0:
        continue

    depth = 0
    for a in prune(resp):
        if args.clusterid:
            docid, score = a
            extract = "foo"
        else:
            extract, docid, score = a
        if docid in pool[qid] and len(pool[qid][docid]) >= args.extperdoc:
            continue
        depth += 1
        if (depth > args.depth):
            break
        if args.clusterid:
            pool[qid].add(docid)
        else:
            if docid not in pool[qid]:
                pool[qid][docid] = set()
            pool[qid][docid].add(extract)

print json.dumps(pool, cls=JSONSetEncoder)
