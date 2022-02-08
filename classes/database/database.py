import psycopg2


class DataBase:
    def __init__(self, dsn):
        self.conn = None
        self.cur = None
        self.dsn = dsn
        self.connect()

    def connect(self):
        params = dict(s.split("=") for s in self.dsn.split())
        self.conn = psycopg2.connect(**params)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def disconnect(self):
        self.cur.close()
        self.conn.close()

    def set(self, querry, *values):
        self.cur.execute(querry, values)

    def get(self, querry, *values):
        self.cur.execute(querry, values)
        return self.cur.fetchall()