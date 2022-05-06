import sqlite3


class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.Connection(path)

    @property
    def tables(self):
        SELECT_TABLES_SQL = "SELECT name FROM sqlite_master WHERE type = 'table';"
        return [x[0] for x in self.connection.execute(SELECT_TABLES_SQL).fetchall()]

    def create(self, table):
        self.connection.execute(table._get_create_sql())

    def save(self, instance):
        sql, values = instance._get_insert_sql()
        cursor = self.connection.execute(sql, values)
        instance._data["id"] = cursor.lastrowid
        self.connection.commit()


