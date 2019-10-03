import json
import datetime
import time

from collections import defaultdict

import req
from pool import pool_status, set_pool_status, get_pool_assignments
from common import get_balance, send_tasks, send_acception


def get_prepared_selections(src_pool, dst_pool, start_ts=None):
    data = get_pool_assignments(src_pool, status='SUBMITTED', start_ts=start_ts)
    res = list()
    mapping = {}
    for page in data['items']:
        for task, boxes in zip(page['tasks'], page['solutions']):
            val = {
                'id': task['id'],
                'input_values': task['input_values'],
                'pool_id': dst_pool,
                'overlap': 3,
            }
            val['input_values']['selection'] = boxes['output_values']['result']
            val['input_values']['assignment_id'] = '2'

            mapping[task['input_values']['image']] = page['id']
            res.append(val)
    return res, mapping


def get_evaluations(start_ts=None):
    data = get_pool_assignments(evaluation_pool, status='ACCEPTED', start_ts=start_ts)

    res = list()
    mapping = {}
    for page in data['items']:
        for task, ans in zip(page['tasks'], page['solutions']):
            val = {
                'image': task['input_values']['image'],
                'ans': ans['output_values'],
            }
            mapping[task['input_values']['image']] = page['id']
            res.append(val)
    return res


def get_decisions(data):
    img_map = defaultdict(list)
    for item in data:
        img_map[item['image']].append(item['ans'])

    min_ok = 2
    decisions = dict()
    for img, answers in img_map.items():
        bads, manys, ins, outs = 0, 0, 0, 0
        for ans in answers:
            bads += ans['ifbad'] == 'OK'
            manys += ans['ifmany'] == 'OK'
            ins += ans['ifin'] == 'OK'
            outs += ans['ifall'] == 'OK'
        decisions[img] = bads >= min_ok and manys >= min_ok and ins >= min_ok and outs >= min_ok
    return decisions


def form_acceptions(decisions, mapping):
    acceptions = defaultdict(int)
    for d, ac in decisions.items():
        if ac:
            acceptions[mapping[d]] += 1
        else:
            acceptions[mapping[d]] -= 1

    for a, val in acceptions.items():
        acceptions[a] = (val > 0)

    return acceptions


def form_new_tasks(img_list, new_pool):
    return [
        {
            'input_values': {'image': img},
            'pool_id': new_pool,
            'overlap': 1
        }
        for img in img_list
    ]


def confirm_pool_start(pool_id):
    print(f"Start pool {pool_id}? [y/n]")
    s = input()
    return s.strip() == 'y'


def first_assignment(image_list, base_pool, evaluation_pool, need_confirm=True):
    next_tasks = form_new_tasks(image_list, base_pool)
    send_tasks(next_tasks)
    start_ts = datetime.datetime.now().isoformat()

    if not need_confirm or confirm_pool_start(base_pool):
        set_pool_status(base_pool, 1)
    else:
        raise KeyboardInterrupt
    while pool_status(base_pool) == 'OPEN':
        time.sleep(10)
    selections = get_prepared_selections(base_pool, evaluation_pool, start_ts)
    return selections[0], selections[1], base_pool


def second_assignment(selections, evaluation_pool, need_confirm=True):
    send_tasks(selections)
    start_ts = datetime.datetime.now().isoformat()
    if not need_confirm or confirm_pool_start(evaluation_pool):
        set_pool_status(evaluation_pool, 1)
    while pool_status(evaluation_pool) == 'OPEN':
        time.sleep(10)
    evaluations = get_evaluations(start_ts)
    decisions = get_decisions(evaluations)
    return decisions


def accept_and_reject(mapping, decisions):
    acceptions = form_acceptions(decisions, mapping)
    for page, res in acceptions.items():
        send_acception(page, res)


def pipeline(img_list, need_confirm=True):
    if get_balance() < 8:
        raise ZeroDivisionError  # :)
    selections, img_page_mapping, new_pool = first_assignment(img_list, base_pool, evaluation_pool, need_confirm)
    decisions = second_assignment(selections, evaluation_pool, need_confirm)
    accept_and_reject(img_page_mapping, decisions)
    unmarked_img_list = [k for k, v in decisions.items() if not v]
    return unmarked_img_list


base_pool = 7383501
evaluation_pool = 7330913
