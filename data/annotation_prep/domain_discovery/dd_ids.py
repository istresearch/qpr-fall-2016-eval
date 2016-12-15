from __future__ import print_function
import json
import os

def file_grabber(init_path):
    out_files = []
    for i in os.listdir(init_path):
        if os.path.isdir(init_path + i):
            for e in os.listdir(init_path + i):
                out_files.append(init_path + i + '/' + e)
        else:
            out_files.append(init_path + i)
    return out_files

georgetown_path = '../../team_submissions/Georgetown/DomainDiscovery/'
uncharted_path = '../../team_submissions/Uncharted/DomainDiscovery/'
isi_path = '../../team_submissions/ISI/DomainDiscovery/'

georgetown_files = file_grabber(georgetown_path)
uncharted_files = file_grabber(uncharted_path)
isi_files = file_grabber(isi_path)

gt_nyu = set()

for _file_ in georgetown_files:
    f = json.loads(open(_file_).read())
    for i in f:
        for ans in i['answer']:
            for e in ans:
                try:
                    if len(str(e)) == 64:
                        gt_nyu.add(e)
                except:
                    continue

unch_hg = set()
unch_jpl = set()
unch_nyu = set()

for _file_ in uncharted_files:
    f = json.loads(open(_file_).read())
    for i in f:
        try:
            for ans in i['answers']:
                for e in ans:
                    if len(str(e)) == 64:
                        if 'HG' in _file_:
                            unch_hg.add(e)
                        if 'JPL' in _file_:
                            unch_jpl.add(e)
                        if 'NYU' in _file_:
                            unch_nyu.add(e)                                                       
        except:
            continue                        

isi_nyu = set()

for _file_ in isi_files:
    f = json.loads(open(_file_).read())
    for i in f:
        for ans in i['answer']:
            for e in ans:
                try:
                    if len(str(e)) == 64:
                        isi_nyu.add(e)
                except:
                    continue            

nyu_combined = isi_nyu.union(gt_nyu, unch_nyu)

if __name__ == "__main__":

    print("Unique Ads Used in Answers:\nNYU - {0}\nHG - {1}\nJPL - {2}" \
           .format(len(nyu_combined), len(unch_hg), len(unch_jpl)))

    with open('nyu_dd_ids.txt','a') as f:
        for i in list(nyu_combined):
            f.write(i + '\n')

    with open('hg_dd_ids.txt','a') as f:
        for i in list(unch_hg):
            f.write(i + '\n')
            
    with open('jpl_dd_ids.txt','a') as f:
        for i in list(unch_jpl):
            f.write(i + '\n')                                   