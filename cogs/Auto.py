import asyncio
import io
import os

import aiohttp
import logging
import json
import datetime
import time
import random

import discord
from discord import app_commands, Webhook
from discord.ext import commands, tasks

from libs.Convert import is_owner


def convert_time(time):
    date_dt = datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%S')
    new_date_dt = date_dt.strftime('%m/%d | %H時')
    return new_date_dt


def convert_diff_time(end_time, cmd_time: datetime):
    date_dt = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')

    cmd_time_tokyo = cmd_time.astimezone(pytz.timezone('Asia/Tokyo')).replace(tzinfo=datetime.timezone.utc)
    date_dt_tokyo = date_dt.replace(tzinfo=datetime.timezone.utc)
    diff = (date_dt_tokyo - cmd_time_tokyo).seconds / 60
    return str(math.floor(diff))


class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.auto_list = []
        self.webhook_list = {}
        self.convert = bot.convert
        self.scheduler_loop.start()

    async def setup(self):
        await self.bot.wait_until_ready()
        self.webhook_list = self.bot.db.get_webhook_list()

    async def send_msg(self, embed, channel):
        self.session = self.session or aiohttp.ClientSession()
        url = self.webhook_list.get(channel)

        if url is None:
            return None

        webhook = Webhook.from_url(url, session=self.session)

        try:
            log_msg = await webhook.send(embed=embed, wait=True)
            return channel, log_msg.id
        except discord.NotFound:
            self.bot.db.del_stage_automatic(channel)
            self.webhook_list.pop(channel)
            return None
        except Exception:
            return None

    async def auto_sending(self):
        if not self.webhook_list:
            await self.setup()

        s_info_1 = self.convert.get_stage_3('regular', False)
        s_info_2 = self.convert.get_stage_3('bankara-challenge', False)
        s_info_3 = self.convert.get_stage_3('bankara-open', False)
        s_info_4 = self.convert.get_stage_3('coop-grouping-regular', False)
        s_info_5 = self.convert.get_fest_3(False)

        s_t = convert_time(str(s_info_1['start_time']).split('+')[0])
        e_t = convert_time(str(s_info_1['end_time']).split('+')[0])

        description = f'**{s_t} ～ {e_t}**\nㅤ'
        images = []
        embed = discord.Embed(description=description, color=discord.Colour.yellow())
        embed.set_author(name='Splatoon3 ステージ情報',
                         icon_url='https://www.nintendo.co.jp/switch/av5ja/assets/images/common/menu/pc/ika.png')

        if not s_info_1['is_fest']:
            # レギュラー
            stage = f'・{s_info_1["stages"][0]["name"]}\n・{s_info_1["stages"][1]["name"]}'
            for n in [s_info_1["stages"][0]["image"], s_info_1["stages"][1]["image"]]:
                images.append(n)
            embed.add_field(name=f'**レギュラーマッチ**',
                            value=f'```\n{stage}\n```',
                            inline=False)
            # description += f'**レギュラーマッチ**\n```\n{stage}\n```\n'

            # バンカラ(チャレンジ)
            stage_2 = f'・{s_info_2["stages"][0]["name"]}\n・{s_info_2["stages"][1]["name"]}'
            for n in [s_info_2["stages"][0]["image"], s_info_2["stages"][1]["image"]]:
                images.append(n)
            embed.add_field(name=f'**バンカラマッチ (チャレンジ)**',
                            value=f'【ルール】**{s_info_2["rule"]["name"]}**\n```\n{stage_2}\n```',
                            inline=False)
            # description += f'**バンカラマッチ (チャレンジ)**\n```\n{stage_2}\n```\n'

            # バンカラ(オープン)
            stage_3 = f'・{s_info_3["stages"][0]["name"]}\n・{s_info_3["stages"][1]["name"]}'
            for n in [s_info_3["stages"][0]["image"], s_info_3["stages"][1]["image"]]:
                images.append(n)
            embed.add_field(name=f'**バンカラマッチ (オープン)**',
                            value=f'【ルール】{s_info_3["rule"]["name"]}\n```\n{stage_3}\n```',
                            inline=False)
            # description += f'**バンカラマッチ (オープン)** - {s_info_3["rule"]["name"]}\n```\n{stage_3}\n```\n'

            embed.set_image(url=random.choice(images))
        else:
            stage_5 = f'・{s_info_5["stages"][0]["name"]}\n・{s_info_5["stages"][1]["name"]}'
            for n in [s_info_5["stages"][0]["image"], s_info_5["stages"][1]["image"]]:
                images.append(n)

            embed.add_field(name='**フェスマッチ**',
                            value=f'```\n{stage_5}\n```',
                            inline=False)
            if s_info_5['is_tricolor']:
                stage_tricolor = f'・{s_info_5["tricolor_stage"]["name"]}'
                embed.add_field(name='トリカラバトル',
                                value=f'```\n{stage_tricolor}\n```')
            embed.set_image(url=random.choice(images))

        stage4 = f'{s_info_4["stage"]["name"]}' if s_info_4["stage"] else "未発表"
        weapons = ''
        if s_info_4['weapons']:
            for we in s_info_4['weapons']:
                weapons += f'・{we["name"]}\n'
        else:
            weapons = '未発表'

        de_msg = f'【ステージ】 {stage4}\n【支給ブキ】\n```\n{weapons}```'
        embed.add_field(name=f'**サーモンラン**',
                        value=f'```\n{de_msg}\n```',
                        inline=False)

        tasks = []
        for channel in self.webhook_list.keys():
            tasks.append(self.send_msg(embed, channel))

        logs = await asyncio.gather(*tasks)

        log_dict = {}
        for log in logs:
            if log is None:
                continue
            log_dict[log[0]] = log[1]

        msg_log = json.dumps(log_dict, ensure_ascii=False, indent=4)
        log_file = discord.File(fp=io.StringIO(msg_log), filename="auto_sending_log.txt")
        log_webhook_url = os.getenv('LOG_WEBHOOK_URL')
        log_webhook = Webhook.from_url(
            log_webhook_url,
            session=self.session
        )
        return await log_webhook.send(content='---logs---', file=log_file)

    @app_commands.command(name='auto-set')
    @app_commands.checks.has_permissions(administrator=True)
    async def auto_setting(self, interaction: discord.Interaction):
        """ステージ情報の定期送信の設定を行います"""
        if not self.webhook_list:
            await self.setup()

        self.auto_list.append(interaction.channel.id)
        if isinstance(interaction.channel, (discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel, discord.StageChannel)):
            return await interaction.response.send_message('テキストチャンネルで実行してください。', ephemeral=True)
        webhook = await interaction.channel.create_webhook(name='スプラトゥーンステージ情報Bot', avatar=(await self.bot.user.avatar.read()))
        webhook_url = f'https://discord.com/api/webhooks/{webhook.id}/{webhook.token}'
        set_data = self.bot.db.set_stage_automatic(interaction.channel.id, webhook_url)
        if not set_data:
            return await interaction.response.send_message('既に設定されています。', ephemeral=True)

        self.webhook_list[interaction.channel.id] = webhook_url

        return await interaction.response.send_message('自動送信の設定が完了しました！', ephemeral=True)

    @auto_setting.error
    async def auto_setting_error(self, interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message(
                content=f'このコマンドを実行するには {error.missing_permissions[0]} の権限が必要です。', ephemeral=True)
        else:
            raise error

    @app_commands.command(name='auto-del')
    @app_commands.checks.has_permissions(administrator=True)
    async def auto_delete(self, interaction: discord.Interaction):
        """ステージ情報の定期送信の設定を削除します"""
        if not self.webhook_list:
            await self.setup()

        data = self.bot.db.get_stage_automatic(interaction.channel.id)

        if not data:
            return await interaction.response.send_message('このチャンネルには設定されていません。', ephemeral=True)
        else:
            self.bot.db.del_stage_automatic(interaction.channel.id)
            self.webhook_list.pop(interaction.channel.id)
            webhooks = await interaction.channel.webhooks()
            webhook = discord.utils.get(webhooks, name='スプラトゥーンステージ情報Bot')
            if webhook:
                await webhook.delete()
            return await interaction.response.send_message('設定を削除しました。', ephemeral=True)

    @auto_delete.error
    async def auto_delete_error(self, interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message(
                content=f'このコマンドを実行するには {error.missing_permissions[0]} の権限が必要です。', ephemeral=True)
        else:
            raise error

    @tasks.loop(hours=2)
    async def scheduler_loop(self):
        await self.auto_sending()


async def setup(bot):
    await bot.add_cog(Auto(bot))
