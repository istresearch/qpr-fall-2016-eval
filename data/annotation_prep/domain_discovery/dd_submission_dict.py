from __future__ import print_function
import os
import argparse
import json
from pyelasticsearch import ElasticSearch
import boto
import smart_open

def get_ads(submission_dict, team, s3_key, s3_secret):
    ads = {}
    _ids = set()

    for kk, vv in submission_dict.iteritems():
        for _id in vv['_ids']:
            _ids.add(_id)
    
    key = boto.connect_s3(aws_access_key_id=s3_key, aws_secret_access_key=s3_secret).get_bucket("memex-fall2016-qpr").get_key("DD_Eval/"+team+"_sorted.jsonl.gz")
    
    with smart_open.smart_open(key) as f:
        for line in f:
            doc = json.loads(line.split('\n')[0])
            _id = doc['_id']
            if _id in _ids:
                ads[_id] = {'_id': _id, 'url': doc['url'], 'extracted_text': doc['extracted_text'], 'img_urls': []}

    return ads

def update_submission_d(pf_set, submission_dict, depth):
    for i in pf_set:
        q_id = i['question_id']
        _id_set = set()
        for ans in i['answer']:
            if len(_id_set) < depth:
                submission_dict[q_id]['_ids'].add(ans[1])
                _id_set.add(ans[1])
                if ans[1] not in submission_dict[q_id]['submissions']:
                    submission_dict[q_id]['submissions'][ans[1]] = [ans[0]]
                else:
                    submission_dict[q_id]['submissions'][ans[1]].append([ans[0]])
            else:
                break

def gen_pf_query(q_id):
    q = {      
         "query": {
            "term": {
            "q_id": int(q_id)
            }
         }
    }
    return q

def get_annotation(es, q_id):
    q = gen_pf_query(q_id)
    res = es.search(query=q, index='memex-fall2016-search', doc_type='annotations', size=1)['hits']['hits'][0]['_source']
    question = res['question']
    answer = res['answer']
    return {'question': question, 
            'answer': answer}

georgetown_path = '../../team_submissions/Georgetown/DomainDiscovery/'
uncharted_path = '../../team_submissions/Uncharted/DomainDiscovery/'
isi_path = '../../team_submissions/ISI/DomainDiscovery/'

def file_grabber(init_path):
    out_files = []
    for i in os.listdir(init_path):
        if os.path.isdir(init_path + i):
            for e in os.listdir(init_path + i):
                out_files.append(init_path + i + '/' + e)
        else:
            out_files.append(init_path + i)
    return out_files

georgetown_files = file_grabber(georgetown_path)
uncharted_files = file_grabber(uncharted_path)
isi_files = file_grabber(isi_path)

for i in georgetown_files:
    if 'aggregate' in i:
        gt_nyu_agg = i
    elif 'CF' in i:
        gt_nyu_cf = i
    elif 'CI' in i:
        gt_nyu_ci = i
    elif 'pointfact' in i:
        gt_nyu_pf = i
        
for i in uncharted_files:
    if 'HG' in i:
        unch_hg = i
    elif 'JPL' in i:
        unch_jpl = i
    elif 'NYU' in i:
        unch_nyu = i

for i in isi_files:
    if 'aggregate' in i:
        isi_nyu_agg = i
    elif 'cluster_facet' in i:
        isi_nyu_cf = i
    elif 'cluster_identification' in i:
        isi_nyu_ci = i
    elif 'point_fact' in i:
        isi_nyu_pf = i        

questions = set()

# read in and normalize georgetown
f = open(gt_nyu_pf, 'r')
georgetown_pf = eval(f.read())
f.close()
for i in georgetown_pf:
    i['question_id'] = i.pop('id')
    questions.add(i['question_id'])

# read in and normalize uncharted
uncharted_pf = []
f = open(unch_nyu, 'r')
pf_inner = [i for i in eval(f.read()) if i['questionType'] == 'Point Fact']
f.close()
for i in pf_inner:
    i.pop('questionType')
    i['answer'] = i.pop('answers') 
    questions.add(i['question_id'])
    uncharted_pf.append(i)

# read in and parse ISI
isi_pf = []
f = open(isi_nyu_pf, 'r')
pf_inner = json.loads(f.read())
f.close()
for i in pf_inner:
    i.pop('SPARQL')
    i.pop('orig_query')
    i.pop('question')
    i.pop('type')
    i['question_id'] = i['question_id'].split('-')[0]
    questions.add(i['question_id'])
    isi_pf.append(i)                                          

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", help="IST ES username")
    parser.add_argument("--password", help="IST ES username")
    parser.add_argument("--s3_key", help="S3 access key")
    parser.add_argument("--s3_secret", help="S3 secret key")
    parser.add_argument("--depth", help="number of ads to consider per submission")
    args = parser.parse_args()

    es = ElasticSearch('https://' + args.user + ':' + args.password + '@ist-es.istresearch.com:9200')

    # build out a dictionary where the key is the question ID
    submission_dict = {}
    for i in questions:
        submission_dict[i] = {'_ids': set(), 'submissions': {}, 'annotation': get_annotation(es, i)}

    update_submission_d(georgetown_pf,submission_dict, args.depth)
    update_submission_d(uncharted_pf,submission_dict, args.depth)
    update_submission_d(isi_pf,submission_dict, args.depth)        

    ads = get_ads(submission_dict, 'nyu', args.s3_key, args.s3_secret)

    for kk, vv in submission_dict.iteritems():
    vv['ads'] = []
    for _id in vv['_ids']:
        if _id in ads:
            vv['ads'].append(ads[_id])