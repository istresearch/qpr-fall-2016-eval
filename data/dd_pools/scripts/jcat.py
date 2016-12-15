#!/usr/bin/env python
import json
import sys

data = sys.stdin.read()
print json.dumps(json.loads(data), sort_keys=True, indent=4)

