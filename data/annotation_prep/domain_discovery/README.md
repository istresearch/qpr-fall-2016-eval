# Domain Discovery Post Hoc

### Obtaining DD `_id`s
The script `dd_ids.py` iterates over all the various teams submissions and generates sets of `_id`s for each DD index:

Each set of `_id`s is then written out as a line separated plain text file per DD team:

* NYU: `nyu_dd_ids.txt`
* Hyperion Gray: `hg_dd_ids.txt`
* JPL: `jpl_dd_ids.txt`


### Sorting DD data
The script `dd_index_sort.py` takes in the output of the `dd_ids.py` files and, for a given team, streams their DD submission to find the correct `_id`s. It is run by passing an `index` (either "hg", "nyu" or "jpl") and S3 credentials:

`python dd_index_sorty.py --index=hg s3_key=xxxx s3_secret=yyyyy`


### Generating Annotation Dictionaries
The script `dd_submission_dict.py` uses the sorted DD index files (saved to S3) and generates dictionaries which are parseable by the annotation UI. It requires access to the ground truth index on ES, the S3 bucket where the sorted DD files are stored, a depth to pool ads per question, and a scope to operate on which is one of `['pf','ci','cf','agg','hg','jpl','all']`. Note that if scope is a question type then only NYU DD index is operated on. If it is a team then that team is operated on; all produces all output.

Each dictionary is saved as a gzipped file. The code is run with:

`python dd_submission_dict.py --host=es.com:port --user=user --password=some_password s3_key=xxxx s3_secret=yyyyy --pf_depth=50 --cluster_depth=100 --scope=all`