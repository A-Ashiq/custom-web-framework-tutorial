class Column:
    def __init__(self, column_type: object):
        self.type = column_type

    @property
    def sql_type(self):
        SQLITE_TYPE_MAP = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bytes: "BLOB",
            bool: "INTEGER",  # 0 or 1
        }
        return SQLITE_TYPE_MAP[self.type]


