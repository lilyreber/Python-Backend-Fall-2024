import math
from http import HTTPStatus

async def app(scope, receive, send) -> None:
    if scope["method"] == "GET":
        path = scope["path"]
        if path == "/factorial":
            await send_factorial(scope, send)
            return
        if path.startswith("/fibonacci"):
            await send_fibonacci(scope, send)
            return
        if path == "/mean":
            await send_mean(scope, send)
            return
    await send_error(send, HTTPStatus.NOT_FOUND)


def get_parameter(scope, param):
    if scope["query_string"]:
        qs = scope["query_string"].decode("utf-8")
        query = dict(entry.split("=") for entry in qs.split("&"))
        return query["n"]

async def send_factorial(scope, send):
    print(scope["query_string"])
    n = get_parameter(scope, "n")
    if not (n and n.isdigit()):
        await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
        return
    n = int(n)
    if n < 0:
        await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
        return

    await send_response(send, HTTPStatus.OK, str(math.factorial(n)))


async def fibonacci(n):
    f0 = 0
    f1 = 1
    for i in range(2, n):
        f0, f1 = f1, f0 + f1
    return f1


async def send_response(send, code, value):
    await send({
        "type": "http.response.start",
        "status": code,
        "headers": [
            [b"content-type", b"text/plain"],
        ]
    })
    await send({
        "type": "http.response.body",
        "body": value,
    })

async def send_error(send, code):
    await send({
        "type": "http.response.start",
        "status": code,
        "headers": [
            [b"content-type", b"text/plain"],
        ]
    })
    await send({
        "type": "http.response.body",
        #"body": message,
    })


