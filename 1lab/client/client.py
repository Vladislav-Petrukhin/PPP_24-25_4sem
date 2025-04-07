import socket
import struct
import logging

from client.logger import setup_client_logger


class ClientApp:
    """
    Простейший клиент, который:
      1) Подключается к серверу
      2) Выполняет аутентификацию
      3) Просит пользователя вводить команды (SELECT ... / GET_JSON / QUIT)
      4) Получает ответ и выводит на экран
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        setup_client_logger()
        self.logger = logging.getLogger("client_logger")

    def run(self):
        """
        Основной метод работы клиента.
        """
        # Подключаемся к серверу
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.logger.info(f"Подключились к серверу {self.host}:{self.port}")

        # Сразу пробуем аутентифицироваться
        self._authenticate()

        # Читаем ответ от сервера - "AUTH_OK" или "AUTH_FAIL"
        auth_result = self._receive_message()
        if auth_result.decode('utf-8') == "AUTH_FAIL":
            self.logger.error("Аутентификация не удалась.")
            self.sock.close()
            return
        elif auth_result.decode('utf-8') == "AUTH_OK":
            self.logger.info("Аутентификация прошла успешно.")

        # Основной цикл ввода команд
        while True:
            command = input("Введите команду (SELECT / GET_JSON / QUIT): ").strip()
            if command.upper() == "QUIT":
                self.logger.info("Завершаем работу клиента.")
                self.sock.close()
                break

            # Отправляем команду на сервер
            self._send_message(command.encode('utf-8'))

            # Получаем ответ
            response = self._receive_message()
            if not response:
                self.logger.warning("Сервер закрыл соединение.")
                break

            # Печатаем ответ
            print("Ответ от сервера:")
            print(response.decode('utf-8'))

        self.sock.close()

    def _authenticate(self):
        """
        Посылаем логин/пароль.
        """
        username = input("Введите имя пользователя: ")
        password = input("Введите пароль: ")
        auth_data = f"{username} {password}"
        self._send_message(auth_data.encode('utf-8'))

    def _send_message(self, message: bytes):
        size_prefix = struct.pack('!I', len(message))
        self.sock.sendall(size_prefix + message)

    def _receive_message(self) -> bytes:
        prefix = self._recv_all(4)
        if not prefix:
            return b""
        message_length = struct.unpack('!I', prefix)[0]
        data = self._recv_all(message_length)
        return data

    def _recv_all(self, length: int) -> bytes:
        buf = b""
        while len(buf) < length:
            chunk = self.sock.recv(length - len(buf))
            if not chunk:
                return b""
            buf += chunk
        return buf
