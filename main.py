import datetime
import requests
import pprint
import time
import hashlib
from data import key, secret, randnum
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
    return ''.join(map(str.strip, txt.split()))


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
    answer = []
    max_len = 0
    for el in stat:
        answer.append([f'Task {el[0]}', f'{el[1] // 3600}:{el[1] % 3600 // 60}', '0'])
        max_len = max(max_len, len(f'Task {el[0]}'), len(f'{el[1] // 3600}:{el[1] % 3600 // 60}'))
    for i in range(1, len(stat)):
        t = stat[i][1] - stat[i - 1][1]
        answer[i][2] = f'{t // 3600}h:{t % 3600 //60}m'
        max_len = max(max_len, len(answer[i][2]))
    print(f'Stats for user "{user_name}"')
    print(' - ' * 40)
    for i in range(3):
        for elem in answer:
            el = elem[i]
            print(el + ' ' * (max_len - len(el) + 2), end='')
        print()
    print(' - ' * 40)


def show_solved_tasks_all():
    global data_from_contest
    solved_tasks = []
    max_len_user = 0
    print('Number of solved tasks')
    print('- ' * 20)
    for key, val in data_from_contest.items():
        tasks = set()
        max_len_user = max(max_len_user, len(key))
        for subs in val:
            tasks.add(subs['problemInd'])
        solved_tasks.append((key, len(tasks)))
    for elem in sorted(solved_tasks, key=lambda el: el[1]):
        print(f"{elem[0]}{(max_len_user - len(elem[0])) * ' '} - solved tasks {elem[1]}")
    print('- ' * 20)
    print(' ' * (max_len_user + 1) + '* * *' + '\n')


def get_data_from_contest(contestId):
    subms = get_submissions_zip(str(contestId) + '.zip')
    apiMethod = 'contest.status'
    _time = int(time.time())
    hApiSig = f"{randnum}/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}#{secret}"
    hash_d = hashlib.sha512(hApiSig.encode())
    hash_hex = hash_d.hexdigest()
    Que = f'https://codeforces.com/api/{apiMethod}?apiKey={key}&asManager=true&contestId={contId}&time={_time}&apiSig={randnum}{hash_hex}'
    query = requests.get(Que)
    attempts = query.json()['result']
    studs = dict()
    for attempt in attempts:
        handle = attempt['author']['members'][0]['handle']
        problem = {'submId': attempt['id'],
                   'timePassed': attempt['relativeTimeSeconds'],
                   'problemInd': attempt['problem']['index'],
                   'problemName': attempt['problem']['name'],
                   'creationTime': attempt['creationTimeSeconds'],
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
    dict_user = {}
    cheat_ans = {}
    for user, subs in data_from_contest.items():
        cur_sub = {}
        for subm in subs:
            cur_sub[subm['problemInd']] = (subm['submText'], subm['timePassed'])
        dict_user[user] = cur_sub
    for task, pair in dict_user[user_name].items():
        prog = pair[0]
        min_time = pair[1]
        verdict = 'Not cheat'
        for user, val in dict_user.items():
            if user == user_name:
                continue
            if task not in val:
                continue
            prog_oth = val[task][0]
            _time_oth = val[task][1]
            if prog == prog_oth and min_time > _time_oth:
                verdict = user
        cheat_ans[task] = verdict
    ans = []
    max_len = 0
    for key, val in cheat_ans.items():
        max_len = max(max_len, len(key), len(val))
        ans.append((key, val))
    ans.sort(key=lambda el: el[0])
    print(f'Cheat answer for user {user_name}')
    for el in ans:
        print(f'{el[0]}:  {el[1]}')
    print('- ' * 20)


def submissions_history(user_name):
    global data_from_contest
    subs = data_from_contest[user_name]
    subslist = []
    for sub in subs:
        subslist.append((sub['problemInd'], sub['creationTime']))
    subslist.sort(key=lambda el: el[1])
    print(f'Submission history for user {user_name}')
    for elem in subslist:
        print(f'{elem[0]}:', end='\t')
        timest = datetime.datetime.fromtimestamp(elem[1])
        print(timest.strftime('%m-%d, %H:%M'))
    print('- ' * 20)


contId = 559532
contests7a = [551176, 553068, 558938]

data_from_contest = get_data_from_contest(contId)
show_solved_tasks_all()
show_stats_all_users()
# show_stats_one_user_many_contests('NikitaAra', contests7a)
compare_subs_one_user('Xieanney')
submissions_history('Xieanney')
