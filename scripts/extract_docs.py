from __future__ import print_function
import smart_open
import boto
import json
import argparse
import gzip
import os
import urllib

doc_url = 'https://s3.amazonaws.com/memex-fall2016-qpr/unpacked/{team}/{id}.gz'
file_path = '/data/ads/{team}/{id}.gz'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ids", help="list of ids to extract")
    args = parser.parse_args()

    cc = 0
    ee = 0
    with open(args.ids, "rb") as ff:
        for ll in ff:
            tt, ii = ll.split(':')
            try:
                url = doc_url.format(team=tt, id=ii)
                file_name = file_path.format(team=tt, id=ii)
                urllib.urlretrieve(url, file_name)
                cc += 1
            except Exception as err:
                print(str(err)) 
                ee += 1
    print("{} ads downloaded; {} failed".format(cc, ee))
