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

    def all(self, table):
        sql, fields = table._get_select_all_sql()

        result = []
        for row in self.connection.execute(sql).fetchall():
            instance = table()
            for field, value in zip(fields, row):
                if field.endswith('_id'):
                    field = field[:-3]
                    fk = getattr(table, field)
                    value = self.get(fk.table, id=value)
                setattr(instance, field, value)
            result.append(instance)

        return result

    def get(self, table, id):
        sql, fields, params = table._get_select_where_sql(id=id)

        row = self.connection.execute(sql, params).fetchone()
        if row is None:
            raise RecordDoesNotExist(f"{table.__name__} instance with id {id} does not exist")

        instance = table()
        for field, value in zip(fields, row):
            if field.endswith('_id'):
                field = field[:-3]
                fk = getattr(table, field)
                value = self.get(fk.table, id=value)
            setattr(instance, field, value)

        return instance

    def update(self, instance):
        sql, values = instance._get_update_sql()
        self.connection.execute(sql, values)
        self.connection.commit()

    def delete(self, table, id):
        sql, params = table._get_delete_sql(id)
        self.connection.execute(sql, params)
        self.connection.commit()


class RecordDoesNotExist(Exception):
    ...