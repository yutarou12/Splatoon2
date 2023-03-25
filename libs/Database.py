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
        self.cursor.execute('CREATE TABLE IF NOT EXISTS command_log(command_name, command_count INTEGER)')
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS premium_data(channel_id INTEGER PRIMARY KEY, guild_id INTEGER, premium, regular, bankara_c, bankara_o, x, salmon)')

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

    def command_log_add(self, command_name):
        self.setup()
        res = self.cursor.execute('SELECT * FROM command_log WHERE command_name=?', (command_name,))
        data = res.fetchall()
        if not data:
            self.cursor.execute('INSERT INTO command_log VALUES (?,?)', (command_name, 1))
        else:
            command_count = int(data[0][1])
            self.cursor.execute('UPDATE command_log SET command_count=? WHERE command_name=?',
                                (command_count + 1, command_name))
        return True

    def premium_data_get(self, guild_id, channel_id):
        self.setup()
        res = self.cursor.execute('SELECT * FROM premium_data WHERE guild_id=?', (guild_id,))
        data = res.fetchall()
        if not data:
            return []
        else:
            raw_data = list()
            for d in data:
                raw_data.append({'channel_id': d[0], 'レギュラー': int(d[3]), 'バンカラC': int(d[4]), 'バンカラO': int(d[5]),
                                 'x': int(d[6]), 'サーモン': int(d[7])})
            return raw_data

    def premium_data_add(self, guild_id, channel_id, data: dict):
        self.setup()
        raw = self.cursor.execute('SELECT premium FROM premium_data WHERE channel_id=?', (channel_id,))
        res = raw.fetchone()
        data_premium = res[0]
        self.cursor.execute('DELETE FROM premium_data WHERE channel_id=?', (channel_id,))

        reg, ban_c, ban_o, x_m, sam = list(data.values())
        self.cursor.execute('INSERT INTO premium_data VALUES (?,?,?,?,?,?,?,?)',
                            (channel_id, guild_id, data_premium, reg, ban_c, ban_o, x_m, sam))

    def premium_new_data(self, guild_id, channel_id):
        self.setup()
        self.cursor.execute('INSERT INTO premium_data VALUES (?,?,?,?,?,?,?,?)',
                            (channel_id, guild_id, 0, 1, 1, 1, 0, 1))
        
    def get_premium_list(self):
        self.setup()
        res = self.cursor.execute('SELECT channel_id FROM premium_data')
        data = res.fetchall()
        
        return [i[0] for i in data]

    def get_premium_data(self, channel_id):
        self.setup()
        res = self.cursor.execute('SELECT * FROM premium_data WHERE channel_id=?', (channel_id,))
        data = res.fetchone()
        if data:
            re_data = {'レギュラー': int(data[3]), 'バンカラC': int(data[4]), 'バンカラO': int(data[5]),
                       'x': int(data[6]), 'サーモン': int(data[7])}
        else:
            re_data = {'レギュラー': 1, 'バンカラC': 1, 'バンカラO': 1, 'x': 0, 'サーモン': 1}

        return re_data

    def del_premium_data(self, channel_id):
        self.setup()
        self.cursor.execute('DELETE FROM premium_data WHERE channel_id=?', (channel_id,))
