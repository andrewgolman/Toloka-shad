import requests

token = open("token").readline()


def get(s):
    return requests.get(
        f'https://toloka.yandex.ru/{s}',
        headers={"Authorization": f"OAuth {token}"}
    )


def post(post, obj):
    return requests.post(
        f'https://toloka.yandex.ru/{post}',
        headers={"Authorization": f"OAuth {token}"},
        json=obj
    )


def patch(post, obj):
    return requests.patch(
        f'https://toloka.yandex.ru/{post}',
        headers={"Authorization": f"OAuth {token}"},
        json=obj
    )
