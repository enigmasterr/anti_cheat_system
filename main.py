import requests
import pprint
import time
import hashlib
from data import key, secret
import os
from zipfile import ZipFile


def get_submissions_from_directory(path): # function to get submissions from directory
    subs = {}
    for fname in os.listdir(path):
        f = open(f"{path}\\{fname}")
        txt = f.read()
        f.close()
        subs[fname.split('.')[0]] = txt
    return subs


def turnNoSpace(txt):
    return ''.join(txt.split())


def get_submissions_zip(fname): # get submissions from zip-archive
    subs = {}
    with ZipFile(fname, 'r') as zpfile:
        for el in zpfile.namelist():
            with zpfile.open(el) as f:
                txt = f.read().decode(encoding="utf-8")
                subs[el.split('.')[0]] = turnNoSpace(txt)
    return subs


def show_stats_one_user(user_name):
    stat = get_stats_one_user(user_name)
    print(f'Stats for user "{user_name}"')
    for el in stat:
        print(f'Task {el[0]}\t', end='')
    print()
    for el in stat:
        print(f'{el[1] // 3600}:{el[1] % 3600 // 60}\t', end='')
    print()
    print('0\t', end='')
    for i in range(1, len(stat)):
        t = stat[i][1] - stat[i - 1][1]
        print(f'{t // 3600}h:{t % 3600 //60}m\t', end='')
    print()
    print('-' * 100)


def show_stats_all_users(): # get dictionary with user names and
    global studs
    for user_name in studs.keys():
        show_stats_one_user(user_name)


def get_stats_one_user(user_name):
    global studs
    subms = studs[user_name]
    tasks = []
    for sub in subms:
        tasks.append((sub['problemInd'], sub['timePassed']))
    return sorted(tasks, key=lambda el: el[1])


def compare_subs_one_user(user_name):
    global studs
    cur_stud = studs[user_name]
    dict_user = {}
    for subm in cur_stud:
        dict_user[subm['problemInd']] = subm['submText']

    for user, data in studs.items():
        if user == user_name:
            continue



contId = 559558
# subms = get_submissions(str(contId))
subms = get_submissions_zip(str(contId) + '.zip')
pprint.pprint(subms)
apiMethod = 'contest.status'
_time = int(time.time())
hApiSig = f"123456/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}#{secret}"
hash_d = hashlib.sha512(hApiSig.encode())
hash_hex = hash_d.hexdigest()
Que = f'https://codeforces.com/api/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}&apiSig=123456{hash_hex}'
query = requests.get(Que)
attempts = query.json()['result']
print(len(query.json()['result']))
pprint.pprint(query.json()['result'][0])
# pprint.pprint(query.json()['result'][0]['author']['members'][0]['handle'])
studs = dict()
for attempt in attempts:
    handle = attempt['author']['members'][0]['handle']
    problem = {'submId': attempt['id'],
               'timePassed': attempt['relativeTimeSeconds'],
               'problemInd': attempt['problem']['index'],
               'problemName': attempt['problem']['name'],
               'submText': ''
               }
    if str(problem['submId']) in subms:
        problem['submText'] = subms[str(problem['submId'])]
    if attempt['verdict'] == 'OK':
        if handle not in studs:
            studs[handle] = []
        studs[handle].append(problem)

pprint.pprint(studs)
for key, val in studs.items():
    print(f"{key} - solved tasks {len(val)}")

show_stats_all_users()
