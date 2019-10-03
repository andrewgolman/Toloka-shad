import requests

token = open("token").readline()


def get(s):
    r = requests.get(
        f'https://toloka.yandex.ru/{s}',
        headers={"Authorization": f"OAuth {token}"}
    )
    print(r)
    if not r.ok:
        print(r.json())
    return r



def post(post, obj):
    r = requests.post(
        f'https://toloka.yandex.ru/{post}',
        headers={"Authorization": f"OAuth {token}"},
        json=obj
    )
    print(r)
    if not r.ok:
        print(r.json())
    return r


def patch(post, obj):
    r = requests.patch(
        f'https://toloka.yandex.ru/{post}',
        headers={"Authorization": f"OAuth {token}"},
        json=obj
    )
    print(r)
    if not r.ok:
        print(r.json())
    return r
