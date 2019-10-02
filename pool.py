import json

import req


def pool_status(pool_id):
    r = req.get(f'/api/v1/pools/{pool_id}')
    s = json.loads(r.text).get('status')
    if not s:
        return json.loads(r.text)
    return s


def set_pool_status(pool_id, change):
    if change == 1:
        s = 'open'
    if change == 0:
        s = 'close'
    r = req.post(f'/api/v1/pools/{pool_id}/{s}', obj=None)
    return json.loads(r.text)


def get_pool_assignments(pool_id):
    return json.loads(req.get(f'/api/v1/assignments?pool_id={pool_id}').text)


def clone_pool(pool_id):
    r = req.post(
        f'/api/v1/pools/{pool_id}/clone',
        None
    )
    op = json.loads(r.text)['id']
    r = req.get(
        f'/api/v1/operations/{op}'
    )
    return int(json.loads(r.text)['details']['pool_id'])
