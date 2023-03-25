import asyncio
import io
import os
import pytz

import aiohttp
import json
import datetime
import random

import discord
from discord import app_commands, Webhook
from discord.ext import commands, tasks


class Auto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.webhook_list = {}
        self.premium_ch_list = list()
        self.convert = bot.convert
        self.utils = bot.utils
        self.scheduler_loop.start()

    async def setup(self):
        await self.bot.wait_until_ready()
        self.webhook_list = self.bot.db.get_webhook_list()
        self.premium_ch_list = self.bot.db.get_premium_list()

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

    def create_msg(self, ch_data: dict, data: list) -> discord.Embed:
        images = list()
        coop_image = list()
        battle_rule_icon = {'ガチヤグラ': '<:battle_gachi_yagura:1054661034268430408>',
                            'ガチエリア': '<:battle_gachi_area:1054661035933573160>',
                            'ガチホコバトル': '<:battle_gachi_hoko:1054661033026932817>',
                            'ガチアサリ': '<:battle_gachi_asari:1054661030564876378>'}

        base_stage, coop, fest = data

        s_t = self.utils.convert_time(str(base_stage['regular']['start_time']).split('+')[0])
        e_t = self.utils.convert_time(str(base_stage['regular']['end_time']).split('+')[0])

        description = f'**{s_t} ～ {e_t}**\nㅤ'
        embed = discord.Embed(description=description, color=discord.Colour.yellow())
        embed.set_author(name='Splatoon3 ステージ情報',
                         icon_url='https://www.nintendo.co.jp/switch/av5ja/assets/images/common/menu/pc/ika.png')

        def msg_regular(all_data):
            info = all_data.get('regular')
            stage = f'・{info["stages"][0]["name"]}\n・{info["stages"][1]["name"]}'
            for n in [info["stages"][0]["image"], info["stages"][1]["image"]]:
                images.append(n)
            embed.add_field(name=f'<:battle_regular:1054319052509687908> **レギュラーマッチ**',
                            value=f'```\n{stage}\n```',
                            inline=False)

        def msg_bankara_c(all_data):
            info = all_data.get('bankara_challenge')
            stage = f'・{info["stages"][0]["name"]}\n・{info["stages"][1]["name"]}'
            for n in [info["stages"][0]["image"], info["stages"][1]["image"]]:
                images.append(n)
            embed.add_field(name=f'<:battle_gachi:1054319050865512509> **バンカラマッチ (チャレンジ)**',
                            value=f'【ルール】**{info["rule"]["name"]}** {battle_rule_icon[info["rule"]["name"]]}'
                                  f'\n```\n{stage}\n```',
                            inline=False)

        def msg_bankara_o(all_data):
            info = all_data.get('bankara_open')
            stage = f'・{info["stages"][0]["name"]}\n・{info["stages"][1]["name"]}'
            for n in [info["stages"][0]["image"], info["stages"][1]["image"]]:
                images.append(n)
            embed.add_field(name=f'<:battle_gachi:1054319050865512509> **バンカラマッチ (オープン)**',
                            value=f'【ルール】**{info["rule"]["name"]}** {battle_rule_icon[info["rule"]["name"]]}'
                                  f'\n```\n{stage}\n```',
                            inline=False)

        def msg_x(all_data):
            info = all_data.get('x')
            stage = f'・{info["stages"][0]["name"]}\n・{info["stages"][1]["name"]}'
            for n in [info["stages"][0]["image"], info["stages"][1]["image"]]:
                images.append(n)
            embed.add_field(name=f'<:battle_x:1053456480575172718> **Xマッチ**',
                            value=f'【ルール】**{info["rule"]["name"]}** {battle_rule_icon[info["rule"]["name"]]}'
                                  f'\n```\n{stage}\n```',
                            inline=False)

        def msg_coop(all_data):
            info = all_data
            stage = f'{info["stage"]["name"]}' if info["stage"] else "未発表"
            coop_image.append(info["stage"]["image"])
            weapons = ''
            if info['weapons']:
                for we in info['weapons']:
                    weapons += f'・{we["name"]}\n'
            else:
                weapons = '未発表'

            embed.add_field(
                name=f'<:battle_salmonrun:1054319424888381444> **{"⚠ ビックラン ⚠" if info["is_big_run"] else "サーモンラン "}**',
                value=f'【ステージ】 {stage}\n【支給ブキ】\n```\n{weapons}```',
                inline=False)

        if not base_stage['regular'].get('is_fest'):
            if ch_data.get('レギュラー'):
                msg_regular(base_stage)
            if ch_data.get('バンカラC'):
                msg_bankara_c(base_stage)
            if ch_data.get('バンカラO'):
                msg_bankara_o(base_stage)
            if ch_data.get('x'):
                msg_x(base_stage)
        else:
            stage_5 = f'・{fest["stages"][0]["name"]}\n・{fest["stages"][1]["name"]}'
            for n in [fest["stages"][0]["image"], fest["stages"][1]["image"]]:
                images.append(n)

            embed.add_field(name='**フェスマッチ**',
                            value=f'```\n{stage_5}\n```',
                            inline=False)
            if fest['is_tricolor']:
                stage_tricolor = f'・{fest["tricolor_stage"]["name"]}'
                embed.add_field(name='トリカラバトル',
                                value=f'```\n{stage_tricolor}\n```')

        if ch_data.get('サーモン'):
            msg_coop(coop)
        if images:
            embed.set_image(url=random.choice(images))
        else:
            if ch_data.get('サーモン'):
                embed.set_image(url=coop_image[0])

        return embed

    async def auto_sending(self):
        await self.setup()
        self.premium_ch_list = self.bot.db.get_premium_list()

        next_stage = self.convert.get_stage_all()
        coop_stage = self.convert.get_stage_3('coop-grouping')
        fest_stage = self.convert.get_fest_3(True)

        next_time = datetime.datetime.strptime(coop_stage["end_time"].split('+')[0], '%Y-%m-%dT%H:%M:%S')
        now_time = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
        if now_time.day == next_time.day and (now_time.hour+1) == next_time.hour:
            coop_info_4 = self.convert.get_stage_3('coop-grouping', True)
        else:
            coop_info_4 = coop_stage

        all_data = [next_stage, coop_info_4, fest_stage]

        tasks = []
        for channel in self.webhook_list.keys():
            data = self.bot.db.get_premium_data(channel)
            embed_data = self.create_msg(ch_data=data, data=all_data)
            tasks.append(self.send_msg(embed_data, channel))

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
    async def auto_setting(self, interaction: discord.Interaction, ch: discord.abc.GuildChannel = None):
        """ステージ情報の定期送信の設定を行います"""
        if not self.webhook_list:
            await self.setup()

        channel = ch if ch else interaction.channel
        data = self.bot.db.premium_data_get(interaction.guild_id, channel.id)

        if len(data) == 2:
            return await interaction.response.send_message('設定できるチャンネルの上限に達しています。', ephemeral=True)

        if isinstance(channel, (discord.VoiceChannel, discord.CategoryChannel, discord.ForumChannel, discord.StageChannel, discord.Thread)):
            return await interaction.response.send_message('テキストチャンネルで実行してください。', ephemeral=True)

        webhook = await channel.create_webhook(name='スプラトゥーンステージ情報Bot', avatar=(await self.bot.user.avatar.read()))
        webhook_url = f'https://discord.com/api/webhooks/{webhook.id}/{webhook.token}'
        set_data = self.bot.db.set_stage_automatic(channel.id, webhook_url)
        if not set_data:
            return await interaction.response.send_message('既に設定されています。', ephemeral=True)

        self.webhook_list[channel.id] = webhook_url
        self.bot.db.premium_new_data(interaction.guild_id, interaction.channel_id)
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
    async def auto_delete(self, interaction: discord.Interaction, ch: discord.abc.GuildChannel = None):
        """ステージ情報の定期送信の設定を削除します"""
        if not self.webhook_list:
            await self.setup()
        channel = ch if ch else interaction.channel
        data = self.bot.db.get_stage_automatic(channel.id)

        if not data:
            return await interaction.response.send_message(f'{channel.mention} には設定されていません。', ephemeral=True)
        else:
            self.bot.db.del_stage_automatic(channel.id)
            self.webhook_list.pop(channel.id)
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
