class AuthManager:
    """
    Простейший менеджер аутентификации.
    В реальном проекте можно хранить пользователей в БД или файле.
    """
    def __init__(self):
        # Допустим, словарь: user -> password
        self.users = {
            "admin": "admin123",
            "user": "pass"
        }

    def check_credentials(self, username: str, password: str) -> bool:
        """
        Возвращает True, если пользователь существует и пароль верен.
        """
        if username in self.users and self.users[username] == password:
            return True
        return False
