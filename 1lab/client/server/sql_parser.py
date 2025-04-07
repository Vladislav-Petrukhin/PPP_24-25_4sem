import re


class SqlParser:
    """
    Простейший парсер, который ищет конструкцию вида:
      SELECT <columns> FROM <table> [WHERE <column> <op> <value>]
    Поддерживаем простые операторы: =, <, >, <=, >=, !=
    """

    def __init__(self):
        # Регулярка на упрощённый SELECT
        self.select_regex = re.compile(
            r"SELECT\s+(?P<columns>[\*\w, ]+)\s+FROM\s+(?P<table>\w+)"
            r"(?:\s+WHERE\s+(?P<where_column>\w+)\s*(?P<operator>=|<|>|<=|>=|!=)\s*(?P<value>[^\s]+))?",
            re.IGNORECASE
        )

    def parse(self, query: str) -> dict:
        match = self.select_regex.match(query)
        if not match:
            raise ValueError(f"Неверный формат запроса: {query}")

        columns_str = match.group("columns").strip()
        table = match.group("table").strip()

        where_column = match.group("where_column")
        operator = match.group("operator")
        value = match.group("value")

        columns = [col.strip() for col in columns_str.split(",")] if columns_str != "*" else ["*"]

        parsed_query = {
            "columns": columns,
            "table": table,
            "where": None
        }

        if where_column and operator and value:
            parsed_query["where"] = {
                "column": where_column,
                "operator": operator,
                "value": value
            }

        return parsed_query
