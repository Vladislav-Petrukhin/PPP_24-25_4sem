import logging
import os

def setup_server_logger(log_file="server.log"):
    """
    Настраиваем логгер для сервера. Вы можете доработать формат, уровень логирования и т.д.
    """
    logger = logging.getLogger("server_logger")
    logger.setLevel(logging.DEBUG)

    # Создаём консольный вывод
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Создаём файл для логов
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # Формат
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    # Можно добавить проверку, чтобы не дублировать хэндлеры при повторной инициализации
