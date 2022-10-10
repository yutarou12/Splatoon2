import sqlite3
dbpath = './db/data.sqlite'
connection = sqlite3.connect(dbpath)
connection.isolation_level = None


class Database:
    def __init__(self):
        self.cursor = connection.cursor()

    def execute(self, sql):
        self.cursor.execute(sql)

    def setup(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS stage_automatic(channel_id integer primary key, webhook_url)')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS friend_code(user_id INTEGER PRIMARY KEY, friend_code, public_code INTEGER)')

    def get_auto_channel(self):
        self.setup()
        self.cursor.execute('SELECT channel_id FROM stage_automatic')

    def get_webhook_list(self):
        self.setup()
        res = self.cursor.execute('SELECT channel_id, webhook_url FROM stage_automatic')
        data = res.fetchall()

        webhook_data = {}
        for i in data:
            channel_id = i[0]
            webhook_url = i[1]
            webhook_data[channel_id] = webhook_url
        return webhook_data

    def set_stage_automatic(self, channel_id, webhook_url):
        self.setup()
        try:
            self.cursor.execute('INSERT INTO stage_automatic VALUES (?, ?)', (channel_id, webhook_url))
            return True
        except sqlite3.IntegrityError:
            return False

    def del_stage_automatic(self, channel_id):
        self.setup()
        self.cursor.execute('DELETE FROM stage_automatic WHERE channel_id = ?', (channel_id,))

    def get_stage_automatic(self, channel_id):
        self.setup()
        res = self.cursor.execute('SELECT * FROM stage_automatic WHERE channel_id = ?', (channel_id,))
        data = res.fetchall()
        return bool(data)

    def friend_code_get(self, user_id):
        self.setup()
        res = self.cursor.execute('SELECT * FROM friend_code WHERE user_id = ?', (user_id,))
        data = res.fetchall()
        return data

    def friend_code_set(self, user_id, friend_code, public: int):
        self.setup()
        self.cursor.execute('INSERT INTO friend_code VALUES (?,?,?)', (user_id, friend_code, public))
        return True

    def friend_code_del(self, user_id):
        self.setup()
        self.cursor.execute('DELETE FROM friend_code WHERE user_id = ?', (user_id,))
        return True

    def friend_code_public(self, user_id, public):
        self.setup()
        self.cursor.execute('UPDATE friend_code SET public_code=? WHERE user_id = ?', (public, user_id))
        return True
