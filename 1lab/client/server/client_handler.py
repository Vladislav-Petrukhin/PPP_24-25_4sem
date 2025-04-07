import logging
import struct
import json

from server.sql_parser import SqlParser
from server.csv_manager import CSVManager
from server.cache_manager import CacheManager
from server.auth_manager import AuthManager


class ClientHandler:
    """
    Класс, обслуживающий конкретного клиента. Получает запросы, обрабатывает их, отправляет ответы.
    """

    def __init__(self, client_socket, client_addr):
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.logger = logging.getLogger("server_logger")

        # Инициализация подсистем
        self.sql_parser = SqlParser()
        self.csv_manager = CSVManager()
        self.cache_manager = CacheManager()
        self.auth_manager = AuthManager()  # Базовая аутентификация

        self.is_authenticated = False

    def run(self):
        """
        Основной цикл работы с клиентом.
        Простейший “протокол”:
          1) сначала клиент пытается аутентифицироваться
          2) затем шлёт команды (SELECT / GET_JSON)
        """
        try:
            self._authenticate()

            if not self.is_authenticated:
                self.logger.warning(f"Клиент {self.client_addr} не прошёл аутентификацию.")
                self._send_message(b"AUTH_FAIL")
                self.client_socket.close()
                return

            # Сообщаем клиенту, что авторизация прошла
            self._send_message(b"AUTH_OK")

            while True:
                data = self._receive_message()
                if not data:
                    self.logger.info(f"Клиент {self.client_addr} разорвал соединение.")
                    break

                # Парсим полученную команду (например: SELECT ... FROM ... WHERE ...)
                # или GET_JSON
                response = self._process_command(data)
                if response is None:
                    # Возможно, команда означает "выход"
                    break
                # Отправим ответ
                self._send_message(response)

        except Exception as e:
            self.logger.exception(f"Ошибка при обработке клиента {self.client_addr}: {e}")
        finally:
            self.client_socket.close()

    def _authenticate(self):
        """
        Базовая схема аутентификации.
        Например, ждём от клиента логин и пароль (простым текстом, или более защищённо — на усмотрение).
        """
        try:
            auth_data = self._receive_message()  # Ожидаем "login:password" или что-то подобное
            if not auth_data:
                return

            login_info = auth_data.decode('utf-8').strip()
            # Предположим, формат "username password"
            parts = login_info.split()
            if len(parts) == 2:
                username, password = parts
                self.is_authenticated = self.auth_manager.check_credentials(username, password)
        except Exception as e:
            self.logger.exception(f"Ошибка при аутентификации клиента {self.client_addr}: {e}")
            self.is_authenticated = False

    def _process_command(self, data: bytes) -> bytes:
        """
        Обрабатываем команду, пришедшую от клиента.
        """
        command_str = data.decode('utf-8').strip()

        # Проверяем, не запрос ли это структуры таблиц
        if command_str.upper() == "GET_JSON":
            json_structure = self.csv_manager.get_tables_structure()
            return json.dumps(json_structure).encode('utf-8')

        # Иначе предполагаем, что это SELECT
        # Парсим запрос
        query_info = self.sql_parser.parse(command_str)  # Возвращает структуру dict

        # Пример структуры:
        # {
        #   "columns": ["*"] или ["id", "name"],
        #   "table": "users",
        #   "where": {
        #       "column": "age",
        #       "operator": ">",
        #       "value": "30"
        #   }
        # }

        # Смотрим, есть ли запрос в кэше
        cached_result = self.cache_manager.get_from_cache(query_info)
        if cached_result is not None:
            self.logger.info("Результат найден в кэше.")
            return cached_result.encode('utf-8')

        # Выполняем чтение CSV
        csv_result = self.csv_manager.select_from_csv(query_info)

        # Сохраняем в кэш
        self.cache_manager.save_to_cache(query_info, csv_result)

        return csv_result.encode('utf-8')

    def _send_message(self, message: bytes):
        """
        Отправляем данные клиенту.
        Можно по-разному упаковывать (struct) для более сложного протокола.
        Здесь — простая отправка длины и тела.
        """
        # Отправляем сначала 4 байта длины
        size_prefix = struct.pack('!I', len(message))
        self.client_socket.sendall(size_prefix + message)

    def _receive_message(self) -> bytes:
        """
        Получаем данные от клиента (читаем 4 байта длины, затем сообщение).
        """
        prefix = self._recv_all(4)
        if not prefix:
            return b""
        message_length = struct.unpack('!I', prefix)[0]
        data = self._recv_all(message_length)
        return data

    def _recv_all(self, length: int) -> bytes:
        """
        Служебный метод для гарантированного чтения n байт из сокета.
        """
        buf = b""
        while len(buf) < length:
            chunk = self.client_socket.recv(length - len(buf))
            if not chunk:
                return b""
            buf += chunk
        return buf
