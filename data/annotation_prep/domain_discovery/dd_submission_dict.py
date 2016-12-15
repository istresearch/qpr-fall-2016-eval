"""

 _| _  _ _  _ . _  
(_|(_)| | |(_||| | 
                   
 _|. _ _ _    _  _ 
(_||_\(_(_)\/(/_|\/
                 / 
 _  _  _ _ _  _    
|_)(_|| _\(/_|     
|                  

"""

from __future__ import print_function
import os
import gzip
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

def update_submission_d(submission_set, submission_type, submission_dict, depth):
    if submission_type == 'pf' or submission_type == 'cf':
        if depth > 10 and submission_type == 'pf':
            depth = 10
        for i in submission_set:
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
                    
    elif submission_type == 'ci':
        for i in submission_set:
            q_id = i['question_id']
            _id_set = set()
            for ans in i['answer']:
                if len(_id_set) < depth:
                    for i in ans:
                        try:
                            if len(str(i)) == 64:
                                _id = i
                        except:
                            continue
                    if _id:
                        submission_dict[q_id]['_ids'].add(_id)
                        _id_set.add(_id)
                        submission_dict[q_id]['submissions'][_id] = []
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

def gen_sparql_query(q_id, q_type=['facet','identification','aggregate']):
    q = { "query" : {
              "constant_score" : { 
                 "filter" : {
                    "bool" : {
                      "must" : [
                         { "term" : {"q_id" : q_id}}, 
                         { "term" : {"q_type" : q_type}} 
                      ]
                      }
                   }
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

def get_annotation_cluster(es, q_id, q_type):
    q = gen_sparql_query(q_id, q_type)
    res = es.search(query=q, index='memex-fall2016-search', doc_type='sparql', size=1)['hits']['hits'][0]['_source']
    question = res['question']
    answer = res.get('value','')
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


###################################
### Read in NYU point fact data ###
###################################
nyu_pf_questions = set()

# read in and normalize georgetown
f = open(gt_nyu_pf, 'r')
georgetown_pf = eval(f.read())
f.close()
for i in georgetown_pf:
    i['question_id'] = i.pop('id')
    nyu_pf_questions.add(i['question_id'])

# read in and normalize uncharted
uncharted_pf = []
f = open(unch_nyu, 'r')
pf_inner = [i for i in eval(f.read()) if i['questionType'] == 'Point Fact']
f.close()
for i in pf_inner:
    i.pop('questionType')
    i['answer'] = i.pop('answers') 
    nyu_pf_questions.add(i['question_id'])
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
    nyu_pf_questions.add(i['question_id'])
    isi_pf.append(i)                                          
###################################
###################################  


###################################
### Read in NYU cluster ID data ###
###################################
nyu_ci_questions = set()

# read in and normalize georgetown
f = open(gt_nyu_ci, 'r')
georgetown_ci = eval(f.read())
f.close()
for i in georgetown_ci:
    i['question_id'] = i.pop('id')
    nyu_ci_questions.add(i['question_id'])

uncharted_ci = []
f = open(unch_nyu, 'r')
ci_inner = [i for i in eval(f.read()) if i['questionType'] == 'Cluster Identification']
f.close()
for i in ci_inner:
    i.pop('questionType')
    nyu_ci_questions.add(i['question_id'])
    if 'answers' in i:
        i['answer'] = i.pop('answers') 
    else:
        i['answer'] = []
    uncharted_ci.append(i)
    
# read in and parse ISI
isi_ci = []
f = open(isi_nyu_ci, 'r')
ci_inner = json.loads(f.read())
f.close()
for i in ci_inner:
    i.pop('SPARQL')
    i.pop('orig_query')
    i.pop('question')
    i.pop('type')
    i['question_id'] = i['question_id'].split('-')[0]
    nyu_ci_questions.add(i['question_id'])
    isi_ci.append(i)   
###################################
###################################


######################################
### Read in NYU cluster facet data ###
######################################
nyu_cf_questions = set()

# read in and normalize georgetown
f = open(gt_nyu_cf, 'r')
georgetown_cf = eval(f.read())
f.close()
for i in georgetown_cf:
    i['question_id'] = i.pop('id')
    nyu_cf_questions.add(i['question_id'])

uncharted_cf = []
f = open(unch_nyu, 'r')
cf_inner = [i for i in eval(f.read()) if i['questionType'] == 'Cluster Facet']
f.close()
for i in cf_inner:
    i.pop('questionType')
    nyu_cf_questions.add(i['question_id'])
    if 'answers' in i:
        i['answer'] = i.pop('answers') 
    else:
        i['answer'] = []
    uncharted_cf.append(i)
    
# read in and parse ISI
isi_cf = []
f = open(isi_nyu_cf, 'r')
cf_inner = json.loads(f.read())
f.close()
for i in cf_inner:
    i.pop('SPARQL')
    i.pop('orig_query')
    i.pop('question')
    i.pop('type')
    i['question_id'] = i['question_id'].split('-')[0]
    nyu_cf_questions.add(i['question_id'])
    isi_cf.append(i)      
###################################
###################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="ES host:port")
    parser.add_argument("--user", help="ES username")
    parser.add_argument("--password", help="ES username")
    parser.add_argument("--s3_key", help="S3 access key")
    parser.add_argument("--s3_secret", help="S3 secret key")
    parser.add_argument("--pf_depth", help="number of ads to consider per submission")
    parser.add_argument("--cluster_depth", help="number of ads to consider per submission")
    parser.add_argument("--scope", help="one of [pf, ci, cf, agg, all]")
    args = parser.parse_args()

    es = ElasticSearch('https://' + args.user + ':' + args.password + '@' + args.host)

    #####################################
    ### Process NYU PF Data into dict ###
    #####################################
    if args.scope == 'pf' or args.scope == 'all':
        print('Building NYU PF Submission Dictionary')
        # build out a dictionary where the key is the question ID
        nyu_pf_d = {}
        for i in nyu_pf_questions:
            nyu_pf_d[i] = {'_ids': set(), 'submissions': {}, 'annotation': get_annotation(es, i)}

        update_submission_d(georgetown_pf, 'pf', nyu_pf_d, args.pf_depth)
        update_submission_d(uncharted_pf, 'pf', nyu_pf_d, args.pf_depth)
        update_submission_d(isi_pf, 'pf', nyu_pf_d, args.pf_depth)        

        ads = get_ads(nyu_pf_d, 'nyu', args.s3_key, args.s3_secret)

        for kk, vv in nyu_pf_d.iteritems():
            vv['ads'] = []
            for _id in vv['_ids']:
                if _id in ads:
                    vv['ads'].append(ads[_id])

        with gzip.open('dd_nyu_pf_dict.json.gz','w') as f:
            for kk, vv in nyu_pf_d.iteritems():
                vv['_ids'] = list(vv['_ids'])
            f.write(json.dumps(nyu_pf_d))
            f.close() 
    #####################################
    #####################################
   

    #####################################
    ### Process NYU CI Data into dict ###
    #####################################
    if args.scope == 'ci' or args.scope == 'all':
        print('Building NYU CI Submission Dictionary')        

        # build out a dictionary where the key is the question ID
        nyu_ci_d = {}
        for i in nyu_ci_questions:
            nyu_ci_d[i] = {'_ids': set(), 'submissions': {}, 'annotation': get_annotation_cluster(es, i, 'identification')}

        update_submission_d(georgetown_ci, 'ci', nyu_ci_d, args.cluster_depth)
        update_submission_d(uncharted_ci, 'ci', nyu_ci_d, args.cluster_depth)
        update_submission_d(isi_ci, 'ci', nyu_ci_d, args.cluster_depth) 
        
        ads = get_ads(nyu_ci_d, 'nyu', args.s3_key, args.s3_secret)
        for kk, vv in nyu_ci_d.iteritems():
            vv['ads'] = []
            for _id in vv['_ids']:
                if _id in ads:
                    vv['ads'].append(ads[_id])       

        with gzip.open('dd_nyu_ci_dict.json.gz','w') as f:
            for kk, vv in nyu_ci_d.iteritems():
                vv['_ids'] = list(vv['_ids'])
            f.write(json.dumps(nyu_ci_d))
            f.close()                 
    #####################################
    #####################################        

    #####################################
    ### Process NYU CF Data into dict ###
    #####################################
    if args.scope == 'cf' or args.scope == 'all':
        print('Building NYU CF Submission Dictionary')        

        # build out a dictionary where the key is the question ID
        nyu_cf_d = {}
        for i in nyu_cf_questions:
            nyu_cf_d[i] = {'_ids': set(), 'submissions': {}, 'annotation': get_annotation_cluster(es, i, 'facet')}

        update_submission_d(georgetown_cf, 'cf', nyu_cf_d, args.cluster_depth)
        update_submission_d(uncharted_cf, 'cf', nyu_cf_d, args.cluster_depth)
        update_submission_d(isi_cf, 'cf', nyu_cf_d, args.cluster_depth) 
        
        ads = get_ads(nyu_cf_d, 'nyu', args.s3_key, args.s3_secret)
        for kk, vv in nyu_cf_d.iteritems():
            vv['ads'] = []
            for _id in vv['_ids']:
                if _id in ads:
                    vv['ads'].append(ads[_id])       

        with gzip.open('dd_nyu_cf_dict.json.gz','w') as f:
            for kk, vv in nyu_cf_d.iteritems():
                vv['_ids'] = list(vv['_ids'])
            f.write(json.dumps(nyu_cf_d))
            f.close()                 
    #####################################
    #####################################        