import time

import req


def pool_status(pool_id):
    r = req.get(f'/api/v1/pools/{pool_id}')
    s = r.json().get('status')
    if not s:
        return r.json()
    return s


def set_pool_status(pool_id, change):
    if change == 1:
        s = 'open'
    if change == 0:
        s = 'close'
    r = req.post(f'/api/v1/pools/{pool_id}/{s}', obj=None)
    return r.json()


def get_pool_assignments(pool_id, status, start_ts=None):
    if start_ts:
        s = '&created_gt=2019-10-03T08:55:19'
    else:
        s = ''
    return req.get(f'/api/v1/assignments?pool_id={pool_id}&status={status}{s}').json()


def clone_pool(pool_id):
    r = req.post(
        f'/api/v1/pools/{pool_id}/clone',
        None
    )
    op = r.json()['id']
    r = req.get(
        f'/api/v1/operations/{op}'
    )
    return int(r.json()['details']['pool_id'])
