import asyncio
import sys
import websockets

async def listen_ws(token: str, host: str = "127.0.0.1", port: int = 8000):
    """
    Подключается к ws://<host>:<port>/ws?token=<token> и выводит все поступающие
    JSON‐сообщения в консоль.
    """
    url = f"ws://{host}:{port}/ws?token={token}"
    print(f"Connecting to {url} …")

    try:
        async with websockets.connect(url) as ws:
            print("Connected. Waiting for messages…\n")
            while True:
                try:
                    msg = await ws.recv()
                    # Просто печатаем «сырое» сообщение
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
    if len(sys.argv) != 2:
        print("Usage: python ws_client.py <JWT_TOKEN>")
        sys.exit(1)

    jwt_token = sys.argv[1]

    asyncio.run(listen_ws(jwt_token))
