import os
import csv
import json
import glob


class CSVManager:
    """
    Класс для управления CSV-файлами.
    Каждый "table" — это папка, внутри которой может быть один или несколько CSV-файлов
    (или один CSV, в зависимости от требований).
    """

    def __init__(self, base_dir="data"):
        self.base_dir = base_dir  # Корневая папка, где лежат папки-таблицы

    def select_from_csv(self, query_info: dict) -> str:
        """
        Выполняет выборку данных из CSV.
        Возвращает результат в виде CSV-строки (для отправки клиенту).
        """
        table_name = query_info["table"]
        columns = query_info["columns"]
        where = query_info["where"]

        table_path = os.path.join(self.base_dir, table_name)
        if not os.path.isdir(table_path):
            raise FileNotFoundError(f"Таблица {table_name} не найдена.")

        # Допустим, ищем все CSV-файлы в папке. Или один конкретный CSV.
        csv_files = glob.glob(os.path.join(table_path, "*.csv"))
        if not csv_files:
            raise FileNotFoundError(f"Нет CSV-файлов в таблице {table_name}.")

        # Собираем все данные
        results = []
        header = None

        for file_path in csv_files:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if header is None:
                    header = reader.fieldnames

                for row in reader:
                    if self._row_matches_condition(row, where):
                        # Если columns = ["*"], берём всё
                        if columns == ["*"]:
                            results.append(row)
                        else:
                            # Берём только нужные колонки
                            filtered_row = {col: row[col] for col in columns if col in row}
                            results.append(filtered_row)

        # Преобразуем results обратно в CSV-формат (строку)
        if not results:
            return "No data\n"

        # Если columns == ['*'] - значит выводим весь header
        if columns == ["*"]:
            columns_to_write = header
        else:
            columns_to_write = columns

        output_lines = []
        output_lines.append(",".join(columns_to_write))

        for r in results:
            line = []
            for c in columns_to_write:
                line.append(r.get(c, ""))  # Если колонки нет, пустое
            output_lines.append(",".join(line))

        return "\n".join(output_lines) + "\n"

    def get_tables_structure(self) -> dict:
        """
        Собирает структуру всех таблиц (папок) и их колонок (из CSV).
        Возвращает словарь для дальнейшего превращения в JSON.
        """
        structure = {}
        # Перебираем все папки в base_dir
        for table_name in os.listdir(self.base_dir):
            table_path = os.path.join(self.base_dir, table_name)
            if os.path.isdir(table_path):
                # Ищем CSV-файлы
                csv_files = glob.glob(os.path.join(table_path, "*.csv"))
                columns_set = set()
                for fp in csv_files:
                    with open(fp, "r", encoding="utf-8") as f:
                        reader = csv.DictReader(f)
                        if reader.fieldnames:
                            columns_set.update(reader.fieldnames)
                structure[table_name] = list(columns_set)
        return structure

    def _row_matches_condition(self, row: dict, where: dict) -> bool:
        """
        Проверяем, проходит ли строка под условие WHERE.
        """
        if not where:
            return True
        col = where["column"]
        op = where["operator"]
        val = where["value"]

        if col not in row:
            return False

        # Для простоты предположим, что все данные — строки,
        # попробуем приводить к float, если возможно.
        row_val_str = row[col]

        # Пытаемся преобразовать оба в float, если не вышло — сравниваем как строки
        try:
            row_val = float(row_val_str)
            condition_val = float(val)
        except ValueError:
            # Сравнение строк
            row_val = row_val_str
            condition_val = val

        # Выполняем операцию
        if op == "=":
            return row_val == condition_val
        elif op == "<":
            return row_val < condition_val
        elif op == ">":
            return row_val > condition_val
        elif op == "<=":
            return row_val <= condition_val
        elif op == ">=":
            return row_val >= condition_val
        elif op == "!=":
            return row_val != condition_val
        else:
            return False
