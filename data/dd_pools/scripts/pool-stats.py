#!/usr/bin/env python

import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file")
args = parser.parse_args()

with open(args.file, "r") as infp:
    pool = json.load(infp)

    s = 0
    
    for qid in pool:
        print qid, len(pool[qid]),
        s += len(pool[qid])
        if len(pool[qid]) > 0 and isinstance(pool[qid], dict):
            print sum([len(pool[qid][d]) for d in pool[qid]]) / float(len(pool[qid]))
        else:
            print
print "Avg", s / len(pool)

