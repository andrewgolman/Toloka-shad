import json

import req


def get_balance():
    r = req.get('/api/v1/requester')
    return json.loads(r.text)['balance']


def send_tasks(selections):
    return json.loads(req.post('/api/v1/tasks?allow_defaults=true', selections).text)


json_acception = [
    {
        "status": "REJECTED",
        "public_comment": "Отклонено после проверки другими исполнителями Толоки: разметка большинства картинок не удовлетворяет инструкции"
    },
    {
        "status": "ACCEPTED",
    },
]


def send_acception(task_id, accept):
    r = req.patch(
        f'api/v1/assignments/{task_id}',
        json_acception[accept]
    )
    if not r.ok:
        print(r.text)
        raise RuntimeError(f"Can't send acception for id={task_id}")
    return r
