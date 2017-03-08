import argparse
import json
import logging

DATA_FILES = [
    ('georgetown', 'jpl', 'data/team_submissions/Georgetown/DomainDiscovery/Georgetown_Submission_2_8/JPL/JPL_Cluster_Facet.json'),
    ('georgetown', 'hg', 'data/team_submissions/Georgetown/DomainDiscovery/Georgetown_Submission_2_8/HG/HG_Cluster_Facet.json'),
    ('georgetown', 'nyu', 'data/team_submissions/Georgetown/DomainDiscovery/NYU_CF.json'),
    ('uncharted', 'jpl', 'data/team_submissions/Uncharted/DomainDiscovery/uncharted_JPL_DD.json'),
    ('uncharted', 'hg', 'data/team_submissions/Uncharted/DomainDiscovery/uncharted_HG_DD.json'),
    ('uncharted', 'nyu', 'data/team_submissions/Uncharted/DomainDiscovery/uncharted_NYU_DD.json'),
    ('isi', 'jpl', 'data/team_submissions/ISI/DomainDiscovery/jpl_answers_isi/properly_formatted_submissions/formatted_cluster-facet-queries-parsed_all_answers.json'),
    ('isi', 'hg', 'data/team_submissions/ISI/DomainDiscovery/hg_all_asnwers/properly_formatted_submissions/formatted_post_cluster_facet_parsed_fixed_all_answers.json'),
    ('isi', 'nyu', 'data/team_submissions/ISI/DomainDiscovery/isi-nyu-answers-dig-extractions/properly_formatted_submissions/formatted_post_cluster_facet_parsed_fixed_all_answers.json'),
]

SEEDS_PATH = 'data/annotation_prep/dd_clustering/FIRST_ROUND_chosen_questions.json'
QUESTIONS_PATH = 'questions/post_cluster_facet.json'

CLUSTER_FILES = (
    'data/annotation_prep/dd_clustering/FIRST_ROUND_seeds2cluster_ads.json',
    'data/annotation_prep/dd_clustering/SECOND_ROUND_seeds2cluster_ads.json'
)

TEAMS = ('georgetown', 'isi', 'uncharted')
CRAWLERS = ('hg', 'jpl', 'nyu')

LOG_LEVELS = {
    'critical': logging.CRITICAL, 
    'error': logging.ERROR, 
    'warning': logging.WARNING, 
    'info': logging.INFO, 
    'debug': logging.DEBUG
}

def get_relevant_questions():
    qq = {}
    logging.debug('opening {}'.format(SEEDS_PATH))
    with open(SEEDS_PATH) as ff:
        data = json.load(ff)
        for kk,vv in data.get('JPL', {}).get('Cluster Facet', {}).items():
            qq[kk] = { 'id': kk, 'seed': vv.get('seed'), 'answers': {} }

    logging.debug('opening {}'.format(QUESTIONS_PATH))
    with open(QUESTIONS_PATH) as ff:
        for ll in ff:
            data = json.loads(ll)
            if data['id'] in qq:
                qq[data['id']]['question'] = data['question']
    return qq

def get_valid_ads(qq):
    seeds = {} 
    for _q in qq:
        seeds[qq[_q]['seed']] = _q
    logging.debug('seeds: {}'.format(seeds))
    for _f in CLUSTER_FILES:
        with open(_f) as ff:
            data = json.load(ff)
            for kk in seeds:
                if kk in data:
                    logging.debug('{} found in {}'.format(kk, _f))
                    if not 'valid' in qq[seeds[kk]]:
                        qq[seeds[kk]]['valid'] = set()
                    for ss in data[kk]:
                        qq[seeds[kk]]['valid'].add(ss)
                else:
                    logging.debug('{} NOT found in {}'.format(kk, _f))
    for _q in qq:
        qq[_q]['valid'] = list(qq[_q]['valid'])
    return qq

def get_team_answers(qq):
    for team, crawler, path in DATA_FILES:  
        for aa in parse_data_file(team, crawler, path):
            if not aa['id'] in qq:
                continue
            if not team in qq[aa['id']]['answers']:
                qq[aa['id']]['answers'][team] = {}
            if not crawler in qq[aa['id']]['answers'][team]:
                qq[aa['id']]['answers'][team][crawler] = []
            for answer in aa['answers']:
                qq[aa['id']]['answers'][team][crawler].append(answer)
    return qq
            
def parse_data_file(team, crawler, path):
    logging.debug('processing {}'.format(path))
    out = []
    with open(path) as ff:
        _in = ff.read()
        if team in ['isi']:
            _in = _in.replace('False', 'false')
            _in = _in.replace('True', 'true')
            _in = _in.replace('None', 'null')
        for ii in json.loads(_in):
            _type = None
            _id = None
            _answers = []
            try:
                _type = ii['type'] if 'type' in ii else ii['questionType']
                _id = ii['id'] if 'id' in ii else ii['question_id']
                _id = _id.split('-')[0]
                _answers = ii['answers'] if 'answers' in ii else ii['answer']
                _answers = _answers[:ARGS['max']]
            except Exception as ee:
                logging.debug(ee)
            if _id and _answers is not None and _type.lower() == 'cluster facet':
                obj = {'id': _id, 'team': team, 'crawler': crawler, 'answers': _answers }
                out.append(obj)
    return out

def collect_docids(qq):
    dd = set()
    for ii in qq:
        for tt in qq[ii]['answers']:
            for cc in qq[ii]['answers'][tt]:
                for aa in qq[ii]['answers'][tt][cc]:
                    dd.add('{}/{}'.format(cc, aa[1]))
    return list(dd)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", "-o", help="path to write JSONL-formatted annotation data", default='cluster_facet_tasks.json')
    parser.add_argument("--ids", "-i", help="path to write list of doc ids", default='docids.txt')
    parser.add_argument("--max", "-m", help="max annotations per team", default=100)
    parser.add_argument("--chunk", "-c", help="max annotations per task", default=20)
    parser.add_argument("--logging", "-l", choices=LOG_LEVELS.keys(), default='info')
    ARGS = vars(parser.parse_args())

    logging.basicConfig(level=LOG_LEVELS[ARGS['logging']])

    questions = get_relevant_questions()
    questions = get_valid_ads(questions)
    questions = get_team_answers(questions)

    logging.debug('questions: {}'.format(json.dumps(questions)))
    
    docids = collect_docids(questions)
    count = 0
    with open(ARGS['ids'], 'wb') as ff:
        for _id in docids:
            ff.write('{}\n'.format(_id))
            count += 1
    logging.info('Wrote {} docids to {}'.format(count, ARGS['ids']))


