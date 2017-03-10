import argparse
import json
import logging

ADS_PATH = '/data/sites/ads/{}/{}.gz'

DATA_FILES = [
    ('georgetown', 'jpl', 'data/team_submissions/Georgetown/DomainDiscovery/Georgetown_Submission_2_8/JPL/JPL_post_aggregate.json'),
    ('georgetown', 'hg', 'data/team_submissions/Georgetown/DomainDiscovery/Georgetown_Submission_2_8/HG/HG_post_aggregate.json'),
    ('georgetown', 'nyu', 'data/team_submissions/Georgetown/DomainDiscovery/NYU_aggregate.json'),
    ('uncharted', 'jpl', 'data/team_submissions/Uncharted/DomainDiscovery/uncharted_JPL_DD.json'),
    ('uncharted', 'hg', 'data/team_submissions/Uncharted/DomainDiscovery/uncharted_HG_DD.json'),
    ('uncharted', 'nyu', 'data/team_submissions/Uncharted/DomainDiscovery/uncharted_NYU_DD.json'),
    ('isi', 'jpl', 'data/team_submissions/ISI/DomainDiscovery/jpl_answers_isi/properly_formatted_submissions/formatted_aggregate-queries-parsed_all_answers.json'),
    ('isi', 'hg', 'data/team_submissions/ISI/DomainDiscovery/jpl_answers_isi/properly_formatted_submissions/formatted_aggregate-queries-parsed_all_answers.json'),
    ('isi', 'nyu', 'data/team_submissions/ISI/DomainDiscovery/isi-nyu-answers-dig-extractions/properly_formatted_submissions/formatted_post_aggregate_parsed_fixed_all_answers.json'),
]

SEEDS_PATH = 'data/annotation_prep/dd_clustering/FIRST_ROUND_chosen_questions.json'
QUESTIONS_PATH = 'questions/post_aggregate_V2.json'

CLUSTER_FILES = (
    'data/annotation_prep/dd_clustering/FIRST_ROUND_seeds2cluster_ads.json',
    'data/annotation_prep/dd_clustering/SECOND_ROUND_seeds2cluster_ads.json'
)

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
        for kk,vv in data.get('JPL', {}).get('Cluster Aggregate', {}).items():
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
        qq[_q]['valid'] = list(qq[_q]['valid']) if 'valid' in qq[_q] else ()
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
                if type(answer).__name__ == 'list':
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
            if _id and _answers is not None:
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

def write_docids(docids):
    count = 0
    with open(ARGS['ids'], 'wb') as ff:
        for _id in docids:
            ff.write('{}\n'.format(_id))
            count += 1
    logging.info('wrote {} docids to {}'.format(count, ARGS['ids']))

def collate_answers(qq):
    tasks = {}
    for ii in qq:
        tasks[ii] = { 'id': qq[ii]['id'], 'question': qq[ii]['question'], 'answers': {} }
        for tt in qq[ii]['answers']:
            for cc in qq[ii]['answers'][tt]:
                for aa in qq[ii]['answers'][tt][cc]:
                    try:
                        open(ADS_PATH.format(cc, aa[1]))
                        adid = '{}:{}'.format(cc, aa[1])
                        answer = (aa[0], tt)
                        if not adid in tasks[ii]['answers']:
                            tasks[ii]['answers'][adid] = []
                        if aa[0] and not answer in tasks[ii]['answers'][adid]:
                            tasks[ii]['answers'][adid].append(answer)
                    except IOError:
                        logging.debug('Skipping {}:{}'.format(cc, aa[1]))
    return tasks

def chunk_tasks(question):
    tasks = []
    aa = question['answers'].items()
    chunks = [aa[ii:ii + ARGS['chunk']] for ii in xrange(0, len(aa), ARGS['chunk'])]
    for cc in chunks:
        qq = question.copy()
        qq['answers'] = dict(cc)
        tasks.append(qq)
    return tasks

def write_tasks(tasks):
    count = 0
    with open(ARGS['out'], 'wb') as ff:
        for qq in tasks:
            for ll in chunk_tasks(tasks[qq]):
                ff.write('{}\n'.format(json.dumps(ll)))
                count += 1
    logging.info('wrote {} tasks to {}'.format(count, ARGS['out']))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", "-o", help="path to write JSONL-formatted annotation data", default='cluster_aggregate_tasks.json')
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
    write_docids(docids)

    tasks = collate_answers(questions)  
    write_tasks(tasks)
        
    #logging.debug('tasks: {}'.format(json.dumps(tasks)))
