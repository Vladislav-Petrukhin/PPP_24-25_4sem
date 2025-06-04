import asyncio
import json
import sys
import websockets

async def listen_ws(token: str, url_to_parse: str, max_depth: int = 3, host: str = "127.0.0.1", port: int = 8000):
    """
    Подключается к ws://<host>:<port>/ws?token=<token>,
    отправляет {"action":"parse","url":url_to_parse,"max_depth":max_depth},
    и выводит все входящие сообщения в консоль.
    """
    url = f"ws://{host}:{port}/ws?token={token}"
    print(f"Connecting to {url} …")

    try:
        async with websockets.connect(url) as ws:
            print("Connected. Sending parse request…\n")

            request = {
                "action": "parse",
                "url": url_to_parse,
                "max_depth": max_depth
            }
            await ws.send(json.dumps(request))
            print(f">>> Sent: {request!r}\n")

            while True:
                try:
                    msg = await ws.recv()
                    print(f">>> Received: {msg}")
                except websockets.ConnectionClosedOK:
                    print("Connection closed by server.")
                    return
                except websockets.ConnectionClosedError as e:
                    print(f"Connection closed with error: {e}")
                    return
                except Exception as e:
                    print(f"Unexpected error while receiving: {e}")
                    return

    except Exception as e:
        print(f"Failed to connect: {e}")


if __name__ == "__main__":
    """
    Запуск:
        python ws_client.py <JWT_TOKEN> <URL_TO_PARSE> [max_depth]
    Пример:
        python ws_client.py eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9… https://books.toscrape.com/ 2
    """
    if not (3 <= len(sys.argv) <= 4):
        print("Usage: python ws_client.py <JWT_TOKEN> <URL_TO_PARSE> [max_depth]")
        sys.exit(1)

    jwt_token = sys.argv[1]
    url_to_parse = sys.argv[2]
    max_depth = int(sys.argv[3]) if len(sys.argv) == 4 else 3

    asyncio.run(listen_ws(jwt_token, url_to_parse, max_depth))
