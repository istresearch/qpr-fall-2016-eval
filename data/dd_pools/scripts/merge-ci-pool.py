#!/usr/bin/env python

import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='+', help='files to merge')
args = parser.parse_args()

pool = None

for f in args.files:
    with open(f, "r") as infp:
        tomerge = json.load(infp)
        if pool is None:
            pool = tomerge
        else:
            for qid in tomerge:
                if qid not in pool:
                    pool[qid] = {}
                tmpset = set(pool[qid])
                tmpset |= set(tomerge[qid])
                pool[qid] = list(tmpset)

print json.dumps(pool)


                    
