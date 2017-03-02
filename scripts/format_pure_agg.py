import argparse
import json
import logging

CRAWLER = 'nyu'

TEAMS = ('georgetown', 'isi', 'uncharted')

LOG_LEVELS = {
    'critical': logging.CRITICAL, 
    'error': logging.ERROR, 
    'warning': logging.WARNING, 
    'info': logging.INFO, 
    'debug': logging.DEBUG
}

def make_tasks(question):
    tasks = []
    aa = question['answers'].items()
    chunks = [aa[ii:ii + args['chunk']] for ii in xrange(0, len(aa), args['chunk'])]
    for cc in chunks:
        qq = question.copy()
        qq['answers'] = dict(cc)
        tasks.append(qq)
    return tasks

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", "-q", help="path to JSONL-formatted question data", required=True)
    parser.add_argument("--out", "-o", help="path to write JSONL-formatted annotation data", required=True)
    parser.add_argument("--ids", "-i", help="path to write list of doc ids", required=True)
    parser.add_argument("--georgetown", help="path to JSONL-formatted answer data submitted by Georgetown", required=True)
    parser.add_argument("--isi", help="path to JSONL-formatted answer data submitted by ISI", required=True)
    parser.add_argument("--uncharted", help="path to JSONL-formatted answer data submitted by Uncharted", required=True)
    parser.add_argument("--max", "-m", help="max annotations per team", default=100)
    parser.add_argument("--chunk", "-c", help="max annotations per task", default=20)
    parser.add_argument("--logging", "-l", choices=LOG_LEVELS.keys(), default='info')
    args = vars(parser.parse_args())

    logging.basicConfig(level=LOG_LEVELS[args['logging']])

    answers = {}
    
    for tt in TEAMS:
        logging.debug('ingesting answers for {}'.format(tt))
        answers[tt] = {}
        with open(args[tt], 'rb') as ff:
            logging.debug('processing {}'.format(args[tt]))
            for ll in ff:
                dd = json.loads(ll)
                qq = str(dd['question_id'])
                answers[tt][qq] = dd
                logging.debug('ingested {}'.format(qq))
    
    annotation_tasks = {}
    logging.debug('ingesting questions')
    with open(args['questions'], 'rb') as ff:
        logging.debug('processing {}'.format(args['questions']))
        for ll in ff:
            data = {}
            dd = json.loads(ll)
            qq = str(dd['id'])
            data = {
                'id': qq,
                'question': dd['question'],
                'answers': {},
            }
            for tt in TEAMS:
                logging.debug('collating answers for {} from {}'.format(qq, tt))
                for aa in answers[tt][qq]['answers'][:args['max']]:
                    _answer = (aa[0], tt)
                    _id = aa[1]
                    if _id and not _id in data['answers']:
                        data['answers'][_id] = set()
                        logging.debug('added answer set for {}'.format(_id))
                    if _answer[0]:
                        data['answers'][_id].add(_answer)
                        logging.debug('added answer to set for {}'.format(_id))
            for aa in data['answers']:
                data['answers'][aa] = list(data['answers'][aa])
            annotation_tasks[qq] = data
            logging.debug('ingested {}'.format(qq))

    doc_ids = set()
    logging.debug('collecting doc ids')
    for tt in annotation_tasks:
        logging.debug('adding doc ids for {}'.format(tt))
        for aa in annotation_tasks[tt]['answers']:
            doc_ids.add(aa)
    with open(args['ids'], 'wb') as ff:
        cc = 0
        for ii in list(doc_ids):
            ff.write('{}:{}\n'.format(CRAWLER, ii))
            cc += 1
        logging.info('Wrote {} document ids to {}'.format(cc, args['ids']))
    with open(args['out'], 'wb') as ff:
        cc = 0
        for tt in annotation_tasks:
            for ll in make_tasks(annotation_tasks[tt]):
                ff.write('{}\n'.format(json.dumps(ll)))
                cc += 1
        logging.info('Wrote {} annotation tasks to {}'.format(cc, args['out']))
