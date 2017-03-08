import json

DOCS_PATH = '/data/ads'
DATA_PATH = '/Users/marti/Desktop'
DATA_FILES = [
    'georgetown_hg_pointfact.json',
    'georgetown_jpl_pointfact.json',
    'georgetown_nyu_pointfact.json',
    'isi_hg_pointfact.json',
    'isi_jpl_all.json',
    'isi_nyu_pointfact.json',
    'uncharted_nyu_all.json',
    'uncharted_hg_all.json',
]
TASK_OUTPUT_FILE = 'combined_pointfact_tasks.json'
DOCID_OUTPUT_FILE = 'docids.txt'
DOCS_PER_TASK = 20
MAX_DOCS_PER_TEAM = 20

QUESTIONS_FILE = 'post_point_fact_V3.json'

QUIDS = (1647, 392, 1707, 217, 510, 799, 363, 1597, 1180, 1159, 1035, 1038, 2304, 1339, 284)

def parse_filename(filename):
    return filename.split('.')[0].split('_')
    
def get_analysis_team(filename):
    return parse_filename(filename)[0]

def get_crawling_team(filename):
    return parse_filename(filename)[1]

def get_collection_type(filename):
    return parse_filename(filename)[2]

def munge(team, ff):
    data = ff.read()
    if team == 'isi':
        data = data.replace('False', 'false').replace('True', 'true')
    data = json.loads(data)
    if team == 'uncharted':
        for kk, vv in enumerate(data):
            if 'answers' in vv:
                vv['answer'] = vv['answers']
                del vv['answers']
    return data

def get_quid(data):
    try:
        return data['id']
    except KeyError:
        return data['question_id'].split('-')[0]

def parse_answer(answer):
    try:    
        return (answer['doc_id'], answer['value'])
    except TypeError:
        return (answer[1], answer[0])

def make_tasks(question):
    tasks = []
    aa = question['answers'].items()
    chunks = [aa[ii:ii + DOCS_PER_TASK] for ii in xrange(0, len(aa), DOCS_PER_TASK)]
    for cc in chunks:
        qq = question.copy()
        qq['answers'] = dict(cc)
        tasks.append(qq)
    return tasks

questions = {}
answers = {}
docids = set()

for filename in DATA_FILES:
    #print filename
    with open('{}/{}'.format(DATA_PATH, filename), 'rb') as ff:
        team = get_analysis_team(filename)
        crawler = get_crawling_team(filename)
        data = munge(team, ff)
        for oo in data:
            id = get_quid(oo)
            if not int(id) in QUIDS:
                continue
            if not id in answers:
                answers[id] = {}
            if not team in answers[id]:
                answers[id][team] = {}
            if not crawler in answers[id][team]:
                answers[id][team][crawler] = {}
            for aa in oo['answer'][:MAX_DOCS_PER_TEAM]:
                _id, _value = parse_answer(aa)
                if not _id in answers[id][team][crawler]:
                    answers[id][team][crawler][_id] = []
                if _value:
                    answers[id][team][crawler][_id].append(_value)

with open('{}/{}'.format(DATA_PATH, QUESTIONS_FILE), 'rb') as ff:
    for ll in ff:
        data = json.loads(ll)
        id = data['id']
        if not int(id) in QUIDS:
            continue
        questions[id] = {
            'id': id,
            'question': data['question'],
            'answers': {}
        }
        for tt in answers[id]:
            for cc in answers[id][tt]:
                for dd in answers[id][tt][cc]:
                    for aa in answers[id][tt][cc][dd]:
                        _id = '{}:{}'.format(cc, dd)
                        docids.add(_id)
                        try:
                            with open('{}/{}/{}.gz'.format(DOCS_PATH, cc, dd)) as _ff:
                                pass
                        except:
                            continue
                        if not _id in questions[id]['answers']:
                            questions[id]['answers'][_id] = set()
                        questions[id]['answers'][_id].add((aa, tt))

for id in questions:
    for _id in questions[id]['answers']:
        questions[id]['answers'][_id] = list(questions[id]['answers'][_id])

with open('{}/{}'.format(DATA_PATH, DOCID_OUTPUT_FILE), 'wb') as ff:
    for id in sorted(list(docids)):
        ff.write('{}\n'.format(id))

with open('{}/{}'.format(DATA_PATH, 'debug.json'), 'wb') as ff:
    ff.write(json.dumps(questions))

with open('{}/{}'.format(DATA_PATH, TASK_OUTPUT_FILE), 'wb') as ff:
    for id in questions:
        for ll in make_tasks(questions[id]):
            ff.write('{}\n'.format(json.dumps(ll)))

