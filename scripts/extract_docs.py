from __future__ import print_function
import smart_open
import boto
import json
import argparse
import gzip
import os

file_path = '/data/ads/{team}/{id}.gz'
s3_path = 'unpacked/{team}/{id}.gz'
BUCKET = 'memex-fall2016-qpr'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", "-i", help="list of ids to extract", required=True)
    parser.add_argument("--key", "-k", help="aws access key", required=True)
    parser.add_argument("--secret", "-s", help="aws secret key", required=True)
    args = parser.parse_args()

    cc = 0
    ee = 0
    bucket = boto.connect_s3(aws_access_key_id=args.key, aws_secret_access_key=args.secret).get_bucket(BUCKET)
    with open(args.ids, "rb") as ff:
        for ll in ff:
            tt, ii = ll.split('\n')[0].split(':')
            try:
                print('Getting {}/{}'.format(tt, ii))
                key_path = s3_path.format(team=tt, id=ii)
                file_name = file_path.format(team=tt, id=ii)
                key = bucket.get_key(key_path)
                with smart_open.smart_open(key) as _in:
                    with gzip.open(file_name, 'wb') as _out:
                        for ll in _in:
                            _out.write(ll)
                cc += 1
            except Exception as err:
                print(str(err))
                ee += 1
    print("{} ads downloaded; {} failed".format(cc, ee))
