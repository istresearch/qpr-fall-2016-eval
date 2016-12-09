from __future__ import print_function
import json
from pyelasticsearch import ElasticSearch
import argparse

def update_submission_d(pf_set, submission_dict):
    for i in pf_set:
        q_id = i['question_id']
        _id_set = set()
        for ans in i['answer']:
            if len(_id_set) < 10:
                submission_dict[q_id]['_ids'].add(ans[1])
                _id_set.add(ans[1])
                if ans[1] not in submission_dict[q_id]['submissions']:
                    submission_dict[q_id]['submissions'][ans[1]] = [ans[0]]
                else:
                    submission_dict[q_id]['submissions'][ans[1]].append([ans[0]])
            else:
                break

def gen_id_query(_ids):
    q = {
      "fields": ["url", "extracted_text"],
      "query": {
          "terms": {
            "_id": _ids
          }   
        }
    }
    return q

def gen_pf_query(q_id):
    q = {      
         "query": {
            "term": {
            "q_id": int(q_id)
            }
         }
    }
    return q

def gen_img_query(_id):
    q = {
      "fields": ["obj_original_url"],
      "query": {
          "term": {
            "obj_parent": _id
            }   
        }
    }
    return q

def get_ads(es, _ids):
    q = gen_id_query(list(_ids))
    res = es.search(query=q, index='memex-fall2016-search', doc_type='escorts', size=len(_ids))['hits']['hits']
    ad_urls = [(i['_id'],i['fields']['url'][0],i['fields']['extracted_text'][0] ) for i in res]
    ad_urls_out = []
    for ad in ad_urls:
        _id = ad[0]
        img_q = gen_img_query(_id)
        imgs = es.search(query=img_q, index='memex-fall2016-search', doc_type='escorts', size=100)['hits']['hits']
        orig_urls = [i['fields']['obj_original_url'][0] for i in imgs]
        ad_urls_out.append([ad[0],ad[1],ad[2],orig_urls])
    return ad_urls_out

def get_annotation(es, q_id):
    q = gen_pf_query(q_id)
    res = es.search(query=q, index='memex-fall2016-search', doc_type='annotations', size=1)['hits']['hits'][0]['_source']
    obj_par = res['obj_parent']
    question = res['question']
    answer = res['answer']
    q_ad = gen_id_query([obj_par])
    orig_ad = es.search(query=q_ad, index='memex-fall2016-search', doc_type='escorts', size=1)['hits']['hits'][0]['fields']['url'][0]
    return {'question': question, 
            'answer': answer, 
            'obj_parent': obj_par, 
            'obj_original_url': orig_ad }

# find the point fact answer sets from each team
georgetown_path = '../../team_submissions/Georgetown/GroundTruth/GT_pointfact.json'
uncharted_path = '../../team_submissions/Uncharted/GroundTruth/'
isi_path = '../../team_submissions/ISI/GroundTruth/'

uncharted_files = ['uncharted_extractions_GT.json',
                   'uncharted_lattice_extractions_CMU_clusters_GT.json',
                   'uncharted_lattice_extractions_GT.json']

isi_files = ['resubmission-isi-ground-truth-2016-11-30/post_point_fact_parsed_fixed_all_answers.json',
             'resubmission-dig-plus-lattice-extractions/post_point_fact_parsed_fixed_all_answers.json',
             'isi-submission-only-lattice-extractions/post_point_fact_parsed_fixed_all_answers.json']

questions = set()

# read in and normalize georgetown
f = open(georgetown_path, 'r')
georgetown_pf = eval(f.read())
f.close()
for i in georgetown_pf:
    i['question_id'] = i.pop('id')
    questions.add(i['question_id'])

# read in and normalize uncharted
uncharted_pf = []
for _file_ in uncharted_files:
    f = open(uncharted_path + _file_, 'r')
    pf_inner = [i for i in eval(f.read()) if i['questionType'] == 'Point Fact']
    f.close()
    for i in pf_inner:
        i.pop('questionType')
        i['answer'] = i.pop('answers') 
        questions.add(i['question_id'])
        uncharted_pf.append(i)

# read in and parse ISI
isi_pf = []
for _file_ in isi_files:
    f = open(isi_path + _file_, 'r')
    pf_inner = eval(f.read())
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
    parser.add_argument("--user", help="start index")
    parser.add_argument("--password", help="stop index")
    args = parser.parse_args()

    es = ElasticSearch('https://' + args.user + ':' + args.password + '@ist-es.istresearch.com:9200')

    # build out a dictionary where the key is the question ID
    submission_dict = {}
    for i in questions:
        submission_dict[i] = {'_ids': set(), 'submissions': {}, 'annotation': get_annotation(es, i)}

    # updated submission dict with each of the teams submissions
    print('building submission dict...\n')
    update_submission_d(georgetown_pf,submission_dict)
    update_submission_d(uncharted_pf,submission_dict)
    update_submission_d(isi_pf,submission_dict)

    # populate the annotation for each question and ad the submitted ads urls
    print('querying ground truth index for ad information...\n')
    for kk, vv in submission_dict.iteritems():
        ads = get_ads(es,vv['_ids'])
        submission_dict[kk]['ads'] = []    
        for _id, url, extracted_text, img_urls in ads:
            submission_dict[kk]['ads'].append({'_id': _id, 'url': url, 'extracted_text': extracted_text, 'img_urls': img_urls})        

    with open('ground_truth_pf_submission_dict.json','w') as f:
        for kk, vv in submission_dict.iteritems():
            vv['_ids'] = list(vv['_ids'])
        f.write(json.dumps(submission_dict))
    f.close()