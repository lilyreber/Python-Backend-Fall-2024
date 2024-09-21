import json
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
        if path.startswith("/mean"):
            await send_mean(scope, receive, send)
            return
    await send_error(send, HTTPStatus.NOT_FOUND)


def get_parameter(scope, param):
    if scope["query_string"]:
        qs = scope["query_string"].decode("utf-8")
        query = dict(entry.split("=") for entry in qs.split("&"))
        return query.get("n")

async def send_factorial(scope, send):
    n = get_parameter(scope, "n")
    try:
        n = int(n)
    except (ValueError, TypeError):
        await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
        return

    if n < 0:
        await send_error(send, HTTPStatus.BAD_REQUEST)
        return

    await send_response(send, HTTPStatus.OK, json.dumps({"result":math.factorial(n)}))


async def send_fibonacci(scope, send):
    n = None
    path_split = scope["path"].split("/")
    if path_split[1] == "fibonacci" and len(path_split) == 3:
        try:
            n = int(path_split[2])
        except ValueError:
            await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
    else:
        await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)

    if n < 0:
        await send_error(send, HTTPStatus.BAD_REQUEST)
        return

    fib = 0
    if n < 2:
        fib = n
    else:
        f0 = 0
        f1 = 1
        for i in range(2, n+1):
            f0, f1 = f1, f0 + f1
        fib = f1
    print(fib)
    await send_response(send, HTTPStatus.OK, json.dumps({"result":fib}))

async def send_mean(scope, receive, send):
    request = await receive()
    body = request.get("body")
    if len(body) == 0:
        await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
        return

    nums = json.loads(body)
    if len(nums) == 0:
        await send_error(send, HTTPStatus.BAD_REQUEST)
        return

    if any(not isinstance(n, (float, int)) for n in nums):
        await send_error(send, HTTPStatus.UNPROCESSABLE_ENTITY)
        return

    await send_response(send, HTTPStatus.OK, json.dumps({"result": sum(nums) / len(nums)}))


async def send_response(send, code, json_value):
    await send({
        "type": "http.response.start",
        "status": code,
        "headers": [
            [b"content-type", b"application/json"],
        ]
    })
    await send({
        "type": "http.response.body",
        "body": json_value.encode("utf-8"),
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


