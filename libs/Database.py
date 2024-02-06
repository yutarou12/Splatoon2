import os
from functools import wraps

import asyncpg
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.pool = None

    async def setup(self):
        self.pool = await asyncpg.create_pool(f"postgresql://{os.getenv('POSTGRESQL_USER')}:{os.getenv('POSTGRESQL_PASSWORD')}@{os.getenv('POSTGRESQL_HOST_NAME')}:{os.getenv('POSTGRESQL_PORT')}/{os.getenv('POSTGRESQL_DATABASE_NAME')}")

        async with self.pool.acquire() as conn:
            await conn.execute('CREATE TABLE IF NOT EXISTS stage_automatic (channel_id bigint PRIMARY KEY, webhook_url)')
            await conn.execute('CREATE TABLE IF NOT EXISTS friend_code(user_id bigint PRIMARY KEY, friend_code, public_code bigint)')
            await conn.execute(
                'CREATE TABLE IF NOT EXISTS command_log(command_name, command_count bigint)')
            await conn.execute(
                'CREATE TABLE IF NOT EXISTS premium_data(channel_id bigint PRIMARY KEY, guild_id bigint, premium, regular, bankara_c, bankara_o, x, salmon)')

        return self.pool

    def check_connection(func):
        @wraps(func)
        async def inner(self, *args, **kwargs):
            self.pool = self.pool or await self.setup()
            return await func(self, *args, **kwargs)

        return inner

    @check_connection
    async def execute(self, sql):
        async with self.pool.acquire() as con:
            await con.execute(sql)

    @check_connection
    async def fetch(self, sql):
        async with self.pool.acquire() as con:
            data = await con.fetch(sql)
        return data

    @check_connection
    async def get_auto_channel(self):
        async with self.pool.acquire() as con:
            data = await con.fetch('SELECT channel_id FROM stage_automatic')
            return data

    @check_connection
    async def get_webhook_list(self):
        async with self.pool.acquire() as con:
            data = await con.fetch('SELECT channel_id, webhook_url FROM stage_automatic')

        webhook_data = {}
        for i in data:
            channel_id = i['channel_id']
            webhook_url = i['webhook_url']
            webhook_data[channel_id] = webhook_url
        return webhook_data

    @check_connection
    async def set_stage_automatic(self, channel_id, webhook_url):
        async with self.pool.acquire() as con:
            try:
                await con.execute('INSERT INTO stage_automatic VALUES ($1, $2)', channel_id, webhook_url)
                return True
            except asyncpg.UniqueViolationError:
                return False

    @check_connection
    async def del_stage_automatic(self, channel_id):
        async with self.pool.acquire() as con:
            await con.execute('DELETE FROM stage_automatic WHERE channel_id = $1', channel_id)

    @check_connection
    async def get_stage_automatic(self, channel_id):
        async with self.pool.acquire() as con:
            data = await con.fetch('SELECT * FROM stage_automatic WHERE channel_id = $1', channel_id)
            return bool(data)

    @check_connection
    async def friend_code_get(self, user_id):
        async with self.pool.acquire() as con:
            data = await con.fetch('SELECT * FROM friend_code WHERE user_id = $1', user_id)
            return data

    @check_connection
    async def friend_code_set(self, user_id, friend_code, public: int):
        async with self.pool.acquire() as con:
            await con.execute('INSERT INTO friend_code VALUES ($1,$2,$3)', user_id, friend_code, public)
            return True

    @check_connection
    async def friend_code_del(self, user_id):
        async with self.pool.acquire() as con:
            await con.execute('DELETE FROM friend_code WHERE user_id = $1', user_id)
            return True

    @check_connection
    async def friend_code_public(self, user_id, public):
        async with self.pool.acquire() as con:
            await con.execute('UPDATE friend_code SET public_code=$1 WHERE user_id = $2', public, user_id)
            return True

    @check_connection
    async def command_log_add(self, command_name):
        async with self.pool.acquire() as con:
            data = await con.fetch('SELECT * FROM command_log WHERE command_name=$1', command_name)
            if not data:
                await con.execute('INSERT INTO command_log VALUES ($1,$2)', command_name, 1)
            else:
                command_count = int(data[0][1])
                await con.execute('UPDATE command_log SET command_count=$1 WHERE command_name=$2', command_count + 1, command_name)
            return True

    @check_connection
    async def premium_data_get(self, guild_id, channel_id):
        async with self.pool.acquire() as con:
            data = await con.execute('SELECT * FROM premium_data WHERE guild_id=$1', guild_id)
            if not data:
                return []
            else:
                raw_data = list()
                for d in data:
                    raw_data.append({'channel_id': d[0], 'レギュラー': int(d[3]), 'バンカラC': int(d[4]), 'バンカラO': int(d[5]),
                                     'x': int(d[6]), 'サーモン': int(d[7])})
                return raw_data

    @check_connection
    async def premium_data_add(self, guild_id, channel_id, data: dict):
        async with self.pool.acquire() as con:
            res = await con.fetch('SELECT premium FROM premium_data WHERE channel_id=$1', channel_id)
            data_premium = res[0]
            await con.execute('DELETE FROM premium_data WHERE channel_id=$1', channel_id)

            reg, ban_c, ban_o, x_m, sam = list(data.values())
            await con.execute('INSERT INTO premium_data VALUES ($1,$2,$3,$4,$5,$6,$7,$8)',
                              channel_id, guild_id, data_premium, reg, ban_c, ban_o, x_m, sam)

    @check_connection
    async def premium_new_data(self, guild_id, channel_id):
        async with self.pool.acquire() as con:
            await con.execute('INSERT INTO premium_data VALUES ($1,$2,$3,$4,$5,$6,$7,$8)',
                                channel_id, guild_id, 0, 1, 1, 1, 0, 1)
        
    @check_connection
    async def get_premium_list(self):
        async with self.pool.acquire() as con:
            data = await con.fetch('SELECT channel_id FROM premium_data')
            return [i[0] for i in data]

    @check_connection
    async def get_premium_data(self, channel_id):
        async with self.pool.acquire() as con:
            data = await con.fetch('SELECT * FROM premium_data WHERE channel_id=$1', channel_id)
            if data:
                re_data = {'レギュラー': int(data[3]), 'バンカラC': int(data[4]), 'バンカラO': int(data[5]),
                           'x': int(data[6]), 'サーモン': int(data[7])}
            else:
                re_data = {'レギュラー': 1, 'バンカラC': 1, 'バンカラO': 1, 'x': 0, 'サーモン': 1}

            return re_data

    @check_connection
    async def del_premium_data(self, channel_id):
        async with self.pool.acquire() as con:
            await con.execute('DELETE FROM premium_data WHERE channel_id=$1', channel_id)
