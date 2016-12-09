# Ground Truth Submissions for Point Fact
The script `pf_post_hoc.py` generates a dictionary of submissions from each teams' run agains the point fact questions.

This dictionary includes teams' top 10 "answer" ads and extractions across each of their runs.

Generate the dictionary by running:
```
python pf_post_hoc.py --user=USERNAME --password=PASSWORD
```
where `user` and `password` are for IST's Elasticsearch cluster.

#### Requirements
`pyelasticsearch==1.4`