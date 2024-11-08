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


def show_solved_tasks_all():
    global data_from_contest
    solved_tasks = []
    for key, val in data_from_contest.items():
        solved_tasks.append((key, len(val)))
    for elem in sorted(solved_tasks, key=lambda el: el[1]):
        print(f"{elem[0]} - solved tasks {elem[1]}")


def get_data_from_contest(contestId):
    subms = get_submissions_zip(str(contestId) + '.zip')
    apiMethod = 'contest.status'
    _time = int(time.time())
    hApiSig = f"123456/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}#{secret}"
    hash_d = hashlib.sha512(hApiSig.encode())
    hash_hex = hash_d.hexdigest()
    Que = f'https://codeforces.com/api/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}&apiSig=123456{hash_hex}'
    query = requests.get(Que)
    attempts = query.json()['result']
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
    return studs


def show_stats_one_user_many_contests(user_name, contests):
    global data_from_contest
    for contest in contests:
        data_from_contest = get_data_from_contest(contest)
        show_stats_one_user(user_name)


def show_stats_all_users(): # get dictionary with user names and
    global data_from_contest
    for user_name in data_from_contest.keys():
        show_stats_one_user(user_name)


def get_stats_one_user(user_name):
    global data_from_contest
    subms = data_from_contest[user_name]
    tasks = []
    for sub in subms:
        tasks.append((sub['problemInd'], sub['timePassed']))
    return sorted(tasks, key=lambda el: el[1])


def compare_subs_one_user(user_name):
    global data_from_contest
    cur_stud = data_from_contest[user_name]
    dict_user = {}
    cheat_ans = {}
    for subm in cur_stud:
        dict_user[subm['problemInd']] = subm['submText']

    for user, data in data_from_contest.items():
        if user == user_name:
            continue
        prog = data['submText']
        ind = data['problemInd']



contId = 553068
contests7a = [551176, 553068, 558938]
# subms = get_submissions(str(contId))
# subms = get_submissions_zip(str(contId) + '.zip')
# pprint.pprint(subms)
# apiMethod = 'contest.status'
# _time = int(time.time())
# hApiSig = f"123456/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}#{secret}"
# hash_d = hashlib.sha512(hApiSig.encode())
# hash_hex = hash_d.hexdigest()
# Que = f'https://codeforces.com/api/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}&apiSig=123456{hash_hex}'
# query = requests.get(Que)
# attempts = query.json()['result']
# print(len(query.json()['result']))
# pprint.pprint(query.json()['result'][0])
# # pprint.pprint(query.json()['result'][0]['author']['members'][0]['handle'])
# studs = dict()
# for attempt in attempts:
#     handle = attempt['author']['members'][0]['handle']
#     problem = {'submId': attempt['id'],
#                'timePassed': attempt['relativeTimeSeconds'],
#                'problemInd': attempt['problem']['index'],
#                'problemName': attempt['problem']['name'],
#                'submText': ''
#                }
#     if str(problem['submId']) in subms:
#         problem['submText'] = subms[str(problem['submId'])]
#     if attempt['verdict'] == 'OK':
#         if handle not in studs:
#             studs[handle] = []
#         studs[handle].append(problem)

data_from_contest = get_data_from_contest(contId)
# pprint.pprint(data_from_contest)
#show_solved_tasks_all()
show_stats_one_user_many_contests('NikitaAra', contests7a)