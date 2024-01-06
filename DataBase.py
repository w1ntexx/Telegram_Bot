import sqlite3 as sq


class DataBase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.con = sq.connect(self.db_path)
            self.cursor = self.con.cursor()
            self.con.commit()
        except sq.Error as e:
            print(f"ERROR connection: {e}")

    def disconnect(self):
        if self.con:
            self.con.close()
            self.con, self.cursor = None, None
            print(f"Database {self.db_path} disconnect")

    def insert(self, table, column: tuple, values: tuple):
        try:
            places = ",".join(["?" for _ in values])
            column_str = ", ".join(column)
            request = f"INSERT INTO {table} ({column_str}) VALUES ({places})"
            self.cursor.execute(request, values)
            self.con.commit()
            print("Inserted successfully")
        except sq.Error as e:
            print(f"ERROR insert: {e}")

    def get(self, table, columns="*", add_request=None):
        try:
            if columns != "*":
                columns = ", ".join(columns)

            requset = f"SELECT {columns} FROM {table}"

            if add_request:
                requset += " " + add_request

            self.cursor.execute(requset)
            return self.cursor.fetchall()
        except sq.Error as e:
            print(f"ERROR get: {e}")
            return None

    def delete_columns(self, table):
        try:
            self.cursor.execute(f"DELETE FROM {table}")
            self.con.commit()
            print("Clear successfully")
        except sq.Error as e:
            print("ERROR delete : {e}")

    def delete_table(self, table):
        try:
            self.cursor.execute(f"DROP TABLE {table}")
            self.con.commit()
            print("Deleted successfully")
        except sq.Error as e:
            print("ERROR delete table: {e}")

    def _reset_all_tables(self, phrases=False):
        self.delete_columns("users")
        self.delete_columns("history")
        if phrases:
            self.delete_columns("phrases")