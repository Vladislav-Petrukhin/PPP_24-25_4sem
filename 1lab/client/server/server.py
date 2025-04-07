import socket
import threading
import logging

from server.client_handler import ClientHandler
from server.logger import setup_server_logger


class Server:
    """
    Класс Server отвечает за создание сокета, прослушивание входящих соединений
    и запуск потоков (или процессов) на каждого клиента.
    """

    def __init__(self, host, port, backlog=5):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.sock = None

        # Инициализируем общий логгер для сервера
        setup_server_logger()  # Допустим, настроим logging
        self.logger = logging.getLogger("server_logger")

    def start(self):
        """
        Запускает сервер: создаём сокет, биндимся, слушаем входящие соединения.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(self.backlog)

        self.logger.info(f"Сервер запущен на {self.host}:{self.port}")

        # Основной цикл приёма клиентов
        while True:
            client_socket, client_addr = self.sock.accept()
            self.logger.info(f"Подключился клиент: {client_addr}")

            # Создаём отдельный поток для обслуживания клиента
            handler_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            handler_thread.start()

    def handle_client(self, client_socket, client_addr):
        """
        Создаём экземпляр ClientHandler и передаём ему управление.
        """
        handler = ClientHandler(client_socket, client_addr)
        handler.run()

    def stop(self):
        """
        Метод для остановки сервера при необходимости.
        """
        if self.sock:
            self.sock.close()
            self.logger.info("Сервер остановлен.")
