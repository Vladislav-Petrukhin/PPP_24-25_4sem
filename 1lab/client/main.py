print("DEBUG: main.py запустился!")

import sys
import argparse

from server.server import Server
from client.client import ClientApp


def main():
    """
    Точка входа в программу.
    Можно вызывать:
        python .\main.py --mode server
    или
        python .\main.py --mode client
    """

    parser = argparse.ArgumentParser(description="File Manager (Server/Client)")
    parser.add_argument("--mode", choices=["server", "client"], required=True,
                        help="Run in server mode or client mode.")

    args = parser.parse_args()

    if args.mode == "server":
        # Запускаем сервер
        server = Server(host='127.0.0.1', port=9090)
        server.start()
    elif args.mode == "client":
        # Запускаем клиент
        client = ClientApp(host='127.0.0.1', port=9090)
        client.run()


if __name__ == "__main__":
    main()
