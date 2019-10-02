import json
import datetime
import time

from collections import defaultdict

import req
from pool import pool_status, set_pool_status, get_pool_assignments, clone_pool
from common import get_balance, send_tasks, send_acception


def get_prepared_selections(pool, start_ts=None):
    data = get_pool_assignments(pool)
    res = list()
    mapping = {}

    for page in data['items']:
        if not page['status'] == 'SUBMITTED':
            continue
        ts = page['submitted']
        if start_ts and ts > start_ts:
            continue
        for task, boxes in zip(page['tasks'], page['solutions']):
            val = {
                'id': task['id'],
                'input_values': task['input_values'],
                'pool_id': second_pool,
                'overlap': 3,
            }
            val['input_values']['selection'] = boxes['output_values']['result']

            mapping[task['input_values']['image']] = page['id']
            res.append(val)
    return res, mapping


def get_evaluations(start_ts=None):
    data = get_pool_assignments(second_pool)

    res = list()
    mapping = {}
    for page in data['items']:
        if not page['status'] == 'ACCEPTED':
            continue
        ts = page['submitted']
        if start_ts and ts > start_ts:
            continue
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

    decisions = dict()
    for img, answers in img_map.items():
        bads, manys, ins, outs = 0, 0, 0, 0
        for ans in answers:
            bads += ans['ifbad'] == 'OK'
            manys += ans['ifmany'] == 'OK'
            ins += ans['ifin'] == 'OK'
            outs += ans['ifout'] == 'OK'
        decisions[img] = bads >= 2 and manys >= 2 and ins >= 2 and outs >= 2
    return img_map


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
        } for img in img_list
    ]


def confirm_pool_start(pool_id):
    print(f"Start pool {pool_id}? [y/n]")
    s = input()
    if s.strip() != 'y':
        return 0
    return 1


def first_assignment(image_list, base_pool, need_confirm=True):
    new_pool = clone_pool(base_pool)
    next_tasks = form_new_tasks(image_list, new_pool)
    send_tasks(next_tasks)
    start_ts = datetime.datetime.now().isoformat()

    if not need_confirm or confirm_pool_start(new_pool):
        set_pool_status(new_pool, 1)
    while pool_status(new_pool) == 'OPEN':
        time.sleep(10)

    selections = get_prepared_selections(new_pool, start_ts)
    return selections[0], selections[1], new_pool


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
    selections, mapping, new_pool = first_assignment(img_list, base_pool, need_confirm)
    decisions = second_assignment(selections, evaluation_pool, need_confirm)
    accept_and_reject(mapping, decisions)
    unmarked_img_list = [k for k, v in decisions.items() if not v]
    return unmarked_img_list


base_pool = 7337247
evaluation_pool = 7330913
