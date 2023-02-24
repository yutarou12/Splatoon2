import os
import random
import requests
import math
import asyncio
import re
import datetime
from typing import Optional

from discord import app_commands, ui
from discord.app_commands import Choice
from discord.ext import commands
import discord

from libs import Page


class Splatoon(commands.Cog):
    """スプラトゥーンステージ情報のコア"""
    def __init__(self, bot):
        self.bot = bot
        self.s_endpoint = 'https://stat.ink/api/v2'
        self.convert = bot.convert
        self.utils = bot.utils

    def create_text(self, info, rule, cmd_time=None):
        s_t = self.utils.convert_time(str(info['start']))
        e_t = self.utils.convert_time(str(info['end']))

        if cmd_time:
            diff_time = self.utils.convert_diff_time(str(info['end']), cmd_time)
        else:
            diff_time = None

        if rule == 'coop':
            stage = info["stage"]["name"] if info["stage"] else "未発表"

            weapons = ''
            if info['weapons']:
                for we in info['weapons']:
                    weapons += f'・{we["name"]}\n'
            else:
                weapons = '未発表'

            if diff_time:
                de_msg = f'**ステージ**\n```\n{stage}\n```\n**支給ブキ**\n```\n{weapons}```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\nあと {diff_time} 分\n```'
            else:
                de_msg = f'**ステージ**\n```\n{stage}\n```\n**支給ブキ**\n```\n{weapons}```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\n```'
        else:
            rule_name = info["rule"]
            stage = f'・{info["maps"][0]}\n・{info["maps"][1]}'

            if diff_time:
                de_msg = f'**ルール**\n```\n{rule_name}```\n**ステージ**\n```\n{stage}\n```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\nあと {diff_time} 分\n```'
            else:
                de_msg = f'**ルール**\n```\n{rule_name}```\n**ステージ**\n```\n{stage}\n```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\n```'

        return de_msg

    def create_text_3(self, info, rule, cmd_time=None):

        s_t = self.utils.convert_time(str(info['start_time']).split("+")[0])
        e_t = self.utils.convert_time(str(info['end_time']).split("+")[0])

        if cmd_time:
            diff_time = self.utils.convert_diff_time(str(info['end_time']).split("+")[0], cmd_time)
        else:
            diff_time = None

        if rule == 'coop-grouping':
            stage = info["stage"]["name"] if info["stage"] else "未発表"

            weapons = ''
            if info['weapons']:
                for we in info['weapons']:
                    weapons += f'・{we["name"]}\n'
            else:
                weapons = '未発表'
            if diff_time:
                de_msg = f'**ステージ**\n```\n{stage}\n```\n**支給ブキ**\n```\n{weapons}```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\nあと {diff_time} 分\n```'
            else:
                de_msg = f'**ステージ**\n```\n{stage}\n```\n**支給ブキ**\n```\n{weapons}```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\n```'
        else:
            rule_name = info["rule"]['name']
            stage = f'・{info["stages"][0]["name"]}\n・{info["stages"][1]["name"]}'

            if diff_time:
                de_msg = f'**ルール**\n```\n{rule_name}```\n**ステージ**\n```\n{stage}\n```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\nあと {diff_time} 分\n```'
            else:
                de_msg = f'**ルール**\n```\n{rule_name}```\n**ステージ**\n```\n{stage}\n```\n' \
                         f'**時間帯**\n```\n{s_t} ～ {e_t}\n```'

        return de_msg

    @app_commands.command(name='stage')
    @app_commands.describe(s_type='ステージ情報を選択してください', s_next_text='時間帯')
    @app_commands.choices(s_type=[Choice(name='レギュラー', value='regular'), Choice(name='ガチ', value='gachi'),
                                  Choice(name='リーグ', value='league'), Choice(name='サーモンラン', value='coop')],
                          s_next_text=[Choice(name='今', value='今'), Choice(name='次', value='次')])
    @app_commands.rename(s_type='ルール', s_next_text='時間帯')
    async def slash_stage(self, interaction, s_type: Choice[str], s_next_text: Choice[str] = '今'):
        """Splatoon2のステージ情報を表示するコマンド"""
        battle_1 = 'https://www.nintendo.co.jp/switch/aab6a/assets/images/battle-sec01_logo.png'
        battle_2 = 'https://www.nintendo.co.jp/switch/aab6a/assets/images/battle-sec02_logo.png'
        battle_3 = 'https://www.nintendo.co.jp/switch/aab6a/assets/images/battle-sec03_logo.png'
        battle_4 = 'https://www.nintendo.co.jp/switch/aab6a/assets/images/salmonrun_catch_kuma.png'

        stage_icon = {'regular': battle_1, 'gachi': battle_2, 'league': battle_3, 'coop': battle_4}
        stage_color = {'regular': 261888, 'gachi': 14840346, 'league': 15409787, 'coop': 15442812}
        stage_time_dict = {'今': False, '次': True}
        stage_time = stage_time_dict[s_next_text if type(s_next_text) == str else s_next_text.name]
        cmd_time = interaction.created_at

        stage_info = self.convert.get_stage(s_type.value, stage_time)
        if s_type.value == 'coop':
            image_url = stage_info['stage']['image']
        else:
            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

        embed = discord.Embed(description=self.create_text(stage_info, s_type.value, cmd_time),
                              color=stage_color[s_type.value])
        embed.set_image(url=image_url)
        embed.set_author(name=f'Splatoon2 | {"サーモンラン " if s_type.value == "coop" else s_type.name + "マッチ"}',
                         icon_url=stage_icon[s_type.value])

        return await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='stage3')
    @app_commands.describe(s_type='ステージ情報を選択してください', s_next_text='時間帯')
    @app_commands.choices(s_type=[Choice(name='レギュラー', value='regular'), Choice(name='バンカラ(チャレンジ)', value='bankara-challenge'),
                                  Choice(name='バンカラ(オープン)', value='bankara-open'), Choice(name='サーモンラン', value='coop-grouping'),
                                  Choice(name='Xマッチ', value='x')],
                          s_next_text=[Choice(name='今', value='今'), Choice(name='次', value='次')])
    @app_commands.rename(s_type='ルール', s_next_text='時間帯')
    async def slash_stage3(self, interaction, s_type: Choice[str], s_next_text: Choice[str] = '今'):
        """Splatoon3のステージ情報を表示するコマンド"""
        battle_1 = 'https://www.nintendo.co.jp/switch/aab6a/assets/images/battle-sec01_logo.png'
        battle_2 = 'https://www.nintendo.co.jp/switch/aab6a/assets/images/battle-sec02_logo.png'
        x_match_icon = 'https://splatoon.syutarou.xyz/images/x_match.png'
        battle_4 = 'https://www.nintendo.co.jp/switch/aab6a/assets/images/salmonrun_catch_kuma.png'

        stage_icon = {'regular': battle_1, 'bankara-challenge': battle_2, 'bankara-open': battle_2,
                      'coop-grouping': battle_4, 'x': x_match_icon}
        stage_name = {'regular': 'レギュラーマッチ', 'bankara-challenge': 'バンカラマッチ (チャレンジ)', 'bankara-open': 'バンカラマッチ (オープン)',
                      'coop-grouping': 'サーモンラン', 'x': 'Xマッチ'}
        stage_color = {'regular': 261888, 'bankara-challenge': 14840346, 'bankara-open': 15409787,
                       'coop-grouping': 15442812, 'x': 53916}
        stage_time_dict = {'今': False, '次': True}
        stage_time = stage_time_dict[s_next_text if type(s_next_text) == str else s_next_text.name]
        cmd_time = interaction.created_at

        stage_info = self.convert.get_stage_3(s_type.value, stage_time)
        # フェス
        if s_type.value == 'coop-grouping':
            image_url = stage_info['stage']['image']

            embed = discord.Embed(description=self.create_text_3(stage_info, s_type.value, cmd_time),
                                  color=stage_color[s_type.value])
            embed.set_author(name=f'Splatoon3 | {"⚠ ビックラン ⚠" if stage_info["is_big_run"] else stage_name[s_type.value]}',
                             icon_url=stage_icon[s_type.value])
            embed.set_image(url=image_url)

            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if stage_info['is_fest']:
                fest_info = self.convert.get_fest_3(stage_time)

                stage = f'・{fest_info["stages"][0]["name"]}\n・{fest_info["stages"][1]["name"]}'
                s_t = self.utils.convert_time(str(fest_info['start_time']).split("+")[0])
                e_t = self.utils.convert_time(str(fest_info['end_time']).split("+")[0])
                diff_time = self.utils.convert_diff_time(str(fest_info['end_time']).split("+")[0], cmd_time)

                if fest_info['is_tricolor']:
                    tricolor = fest_info['tricolor_stage']
                    de_msg = f'**ステージ**\n```\n{stage}\n```\n' \
                             f'**トリカラステージ**\n```\n{tricolor["name"]}\n```' \
                             f'**時間帯**\n```\n{s_t} ～ {e_t}\n {"あと"+diff_time+"分" if diff_time else ""}\n```'
                    image_url = random.choice([fest_info['stages'][0]['image'], fest_info['stages'][1]['image'], tricolor['image']])

                else:
                    de_msg = f'**ステージ**\n```\n{stage}\n```\n' \
                             f'**時間帯**\n```\n{s_t} ～ {e_t}\n{"あと"+diff_time+"分" if diff_time else ""}\n```'
                    image_url = random.choice(
                        [fest_info['stages'][0]['image'], fest_info['stages'][1]['image']])

                embed = discord.Embed(description=de_msg)
                embed.set_author(name=f'Splatoon3 | フェスマッチ')
                embed.set_image(url=image_url)
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                image_url = random.choice([stage_info['stages'][0]['image'], stage_info['stages'][1]['image']])

                embed = discord.Embed(description=self.create_text_3(stage_info, s_type.value, cmd_time),
                                      color=stage_color[s_type.value])
                embed.set_author(name=f'Splatoon3 | {stage_name[s_type.value]}',
                                 icon_url=stage_icon[s_type.value])
                embed.set_image(url=image_url)

                view = ViewStage(stage_info=stage_info)
                view.add_item(discord.ui.Button(
                    label='図面-説明', style=discord.ButtonStyle.url, url='https://note.com/sunfish3/n/nc029f8edb031'))
                return await interaction.response.send_message(embed=embed, ephemeral=True, view=view)

    async def weapon_lottery(self, interaction: discord.Interaction, version: str):
        weapon = self.convert.get_weapon(version)
        if version == 'v2':
            weapon_list_jp = [(i['name']['ja_JP'], i['splatnet']) for i in weapon]
        else:
            weapon_list_jp = [(i['name']['ja_JP'], i['key']) for i in weapon]

        weapons = random.sample(weapon_list_jp, 6)
        base_path = f'./images/weapons/{version}'
        weapon_files = list()
        for f in weapons:
            if not os.path.exists(f'{base_path}/{f[1]}.png'):
                new_weapon = random.choice(weapon_list_jp)
                if os.path.exists(f'{base_path}/{new_weapon[1]}.png'):
                    weapon_files.append(discord.File(f'{base_path}/{new_weapon[1]}.png', filename='image.png'))
                else:
                    pass
            else:
                weapon_files.append(
                    discord.File(f'{base_path}/{f[1]}.png', filename='image.png'))

        embed = discord.Embed(title='ブキガチャ',
                              description='今の君におススメなのは...')
        embed.set_image(url='attachment://image.png')
        await interaction.response.send_message(embed=embed, files=[weapon_files[0]])

        await asyncio.sleep(1)

        for i in range(1, len(weapon_files)):
            await interaction.edit_original_response(embed=embed, attachments=[weapon_files[i]])
            await asyncio.sleep(1)

        ch_weapon_name, ch_weapon_id = (None, None)
        while True:
            w_name, w_id = random.choice(weapon_list_jp)
            if os.path.exists(f'{base_path}/{w_id}.png'):
                ch_weapon_name, ch_weapon_id = w_name, w_id
                break
            else:
                continue

        file = discord.File(f'{base_path}/{ch_weapon_id}.png', filename='image.png')

        if version == 'v2':
            embed = discord.Embed(title='ブキガチャ 結果',
                                  description=f'今の {interaction.user.mention} におススメなのは...\n**{ch_weapon_name}** でし！\n')
        else:
            embed = discord.Embed(title='ブキガチャ 結果',
                                  description=f'今の {interaction.user.mention} におススメなのは...\n**{ch_weapon_name}** でし！'
                                              f'\n沢山かわいがって強くなって欲しいでし！')
        embed.set_image(url='attachment://image.png')

        await asyncio.sleep(1.5)
        return await interaction.edit_original_response(attachments=[file], embed=embed)

    @app_commands.command(name='weapon')
    @app_commands.checks.cooldown(1, 60*60*2)
    async def slash_weapon(self, interaction):
        """ブキガチャコマンド"""
        await self.weapon_lottery(interaction, 'v2')

    @slash_weapon.error
    async def slash_weapon_error(self, ctx, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await ctx.response.send_message(f'{math.floor(error.retry_after / 60)} 分後にまた良い武器を提案するでし！', ephemeral=True)
        else:
            raise error

    @app_commands.command(name='weapon3')
    @app_commands.checks.cooldown(1, 60 * 60 * 2)
    async def slash_weapon3(self, interaction):
        """ブキガチャコマンド"""
        await self.weapon_lottery(interaction, 'v3')

    @slash_weapon3.error
    async def slash_weapon3_error(self, ctx, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await ctx.response.send_message(f'{math.floor(error.retry_after / 60)} 分後にまた良い武器を提案するでし！', ephemeral=True)
        else:
            raise error

    @app_commands.command(name='list')
    async def stage_list(self, ctx):
        """スプラトゥーンステージ情報の一覧を表示するコマンド"""
        await ctx.response.defer(ephemeral=True)
        stage_color = {'レギュラー': 261888, 'ガチ': 14840346, 'リーグ': 15409787, 'サーモンラン': 15442812}
        r_stage_info = self.convert.get_stage('regular', stage_all=True)
        g_stage_info = self.convert.get_stage('gachi', stage_all=True)
        l_stage_info = self.convert.get_stage('league', stage_all=True)
        c_stage_info = self.convert.get_stage('coop', stage_all=True)

        battle_1 = self.bot.get_emoji(1021769457221255228)
        battle_2 = self.bot.get_emoji(1021769458987057233)
        battle_3 = self.bot.get_emoji(1021769461335859311)
        battle_4 = self.bot.get_emoji(1021769464221540392)

        regular_page = []
        for info in r_stage_info:
            embed = discord.Embed(title=f'{battle_1 if battle_1 else ""}  Splatoon2 | レギュラーマッチ',
                                  description=self.create_text(info, 'regular'),
                                  color=stage_color['レギュラー'])
            embed.set_image(url=random.choice([info['maps_ex'][0]['image'], info['maps_ex'][1]['image']]))
            regular_page.append(embed)

        gachi_page = []
        for info in g_stage_info:
            embed = discord.Embed(title=f'{battle_2 if battle_2 else ""} Splatoon2 | ガチマッチ',
                                  description=self.create_text(info, 'gachi'),
                                  color=stage_color['ガチ'])
            embed.set_image(url=random.choice([info['maps_ex'][0]['image'], info['maps_ex'][1]['image']]))
            gachi_page.append(embed)

        league_page = []
        for info in l_stage_info:
            embed = discord.Embed(title=f'{battle_3 if battle_3 else ""} Splatoon2 | リーグマッチ',
                                  description=self.create_text(info, 'league'),
                                  color=stage_color['リーグ'])
            embed.set_image(url=random.choice([info['maps_ex'][0]['image'], info['maps_ex'][1]['image']]))
            league_page.append(embed)

        coop_page = []
        for info in c_stage_info:
            embed = discord.Embed(title=f'{battle_4 if battle_4 else ""} Splatoon2 | サーモンラン',
                                  description=self.create_text(info, 'coop'),
                                  color=stage_color['サーモンラン'])
            if info['stage']:
                embed.set_image(url=info['stage']['image'])
            coop_page.append(embed)

        page_groups = [
            Page.PageGroup(
                pages=regular_page,
                label="レギュラーマッチ",
                description="レギュラーマッチのステージ一覧",
                emoji=battle_1
            ),
            Page.PageGroup(
                pages=gachi_page,
                label="ガチマッチ",
                description="ガチマッチのステージ一覧",
                emoji=battle_2
            ),
            Page.PageGroup(
                pages=league_page,
                label="リーグマッチ",
                description="リーグマッチのステージ一覧",
                emoji=battle_3
            ),
            Page.PageGroup(
                pages=coop_page,
                label="サーモンラン",
                description="サーモンランのステージ一覧",
                emoji=battle_4
            ),
        ]

        paginator = Page.Paginator(pages=page_groups, show_menu=True)
        await paginator.respond(ctx, ephemeral=True)

    @app_commands.command(name='friend')
    @app_commands.describe(user='ユーザーを選択してください。')
    @app_commands.rename(user='ユーザー')
    async def friends_slash(self, interaction: discord.Interaction, user: Optional[discord.Member]):
        """フレンドコードを表示/検索するコマンド"""
        if not user:
            user_data = self.bot.db.friend_code_get(interaction.user.id)
            if not user_data:
                return await interaction.response.send_message(
                    'フレンドコードが登録されていません!\n`/friend-setting set フレンドコード` で登録できます。', ephemeral=True)
            if user_data[0][2] == 0:
                return await interaction.response.send_message(f'{interaction.user} のフレンドコード\n> {user_data[0][1]}')
            else:
                return await interaction.response.send_message(
                    f'{interaction.user} のフレンドコード\n> {user_data[0][1]}', ephemeral=True)

        else:
            user_data = self.bot.db.friend_code_get(user.id)
            if not user_data:
                return await interaction.response.send_message(
                    f'{user} はフレンドコードを登録していないみたいです!', ephemeral=True)
            if user_data[0][2] == 0:
                return await interaction.response.send_message(
                    f'{interaction.user} のフレンドコード\n> {user_data[0][1]}', ephemeral=True)
            else:
                return await interaction.response.send_message(
                    f'{user} はフレンドコードを非公開設定にしているみたいです!', ephemeral=True)

    @app_commands.guild_only()
    class MyGroup(app_commands.Group):
        pass

    friend_group = MyGroup(name='friend-setting', description='フレンドコードについての設定をするコマンド')
    
    @friend_group.command(name='登録')
    @app_commands.rename(arg='フレンドコード')
    async def friends_set_slash(self, interaction: discord.Interaction, arg: str):
        """フレンドコードを登録します
        
        Parameters
        -----------
        :type interaction: object
        :param arg: フレンドコード
        """
        if not arg:
            return await interaction.response.send_message('フレンドコードを入力してください!\n例: `SW-1234-5678-9012`',
                                                           ephemeral=True)

        match_arg = re.match(r'[a-zA-Z]{2}-\d{4}-\d{4}-\d{4}', arg)
        if not match_arg:
            return await interaction.response.send_message('フレンドコードを正しく入力してください!\n例: `SW-1234-5678-9012`',
                                                           ephemeral=True)

        user_data = self.bot.db.friend_code_get(interaction.user.id)
        if user_data:
            return await interaction.response.send_message('フレンドコードが既に登録されています。', ephemeral=True)
        else:
            self.bot.db.friend_code_set(interaction.user.id, arg, 1)
            return await interaction.response.send_message(f'フレンドコードを `{arg}` で登録しました!', ephemeral=True)

    @friend_group.command(name='削除')
    async def friends_del_slash(self, interaction: discord.Interaction):
        """フレンドコードの設定を削除します"""

        user_data = self.bot.db.friend_code_get(interaction.user.id)
        if not user_data:
            return await interaction.response.send_message(
                'フレンドコードは登録されていません!\n`/friend-setting set フレンドコード` で登録できます。', ephemeral=True)

        res = self.bot.db.friend_code_del(interaction.user.id)
        if res:
            return await interaction.response.send_message('フレンドコードの設定を削除しました!', ephemeral=True)
        else:
            return await interaction.response.send_message('削除に失敗しました', ephemeral=True)

    @friend_group.command(name='公開非公開')
    async def friends_public_slash(self, interaction: discord.Interaction):
        """フレンドコードの公開範囲の設定をします"""

        user_data = self.bot.db.friend_code_get(interaction.user.id)
        if not user_data:
            return await interaction.response.send_message(
                'フレンドコードは登録されていません!\n`/friend-setting set フレンドコード` で登録できます。', ephemeral=True)

        if user_data[0][2] == 0:
            res = self.bot.db.friend_code_public(interaction.user.id, 1)
            if res:
                return await interaction.response.send_message(
                    'フレンドコードを非公開設定にしました。\n他のユーザーからは検索できず、`/friend`は非表示メッセージで送信されます。',
                    ephemeral=True)
        elif user_data[0][2] == 1:
            res = self.bot.db.friend_code_public(interaction.user.id, 0)
            if res:
                return await interaction.response.send_message(
                    'フレンドコードを公開設定にしました。\n他のユーザーは検索が可能になり、`/friend`は通常メッセージで送信されます。',
                    ephemeral=True)
        else:
            return None


class ViewStage(ui.View):
    def __init__(self, stage_info):
        super().__init__()
        self.stage_info = stage_info

    @ui.button(label='ステージ画像', style=discord.ButtonStyle.blurple)
    async def stage_image_button(self, interaction: discord.Interaction, button: ui.Button):
        embed_1 = discord.Embed(description=self.stage_info['stages'][0]['name'])
        embed_1.set_image(url=self.stage_info['stages'][0]['image'])
        embed_2 = discord.Embed(description=self.stage_info['stages'][1]['name'])
        embed_2.set_image(url=self.stage_info['stages'][1]['image'])
        await interaction.response.send_message('ステージ画像', embeds=[embed_1, embed_2], ephemeral=True)

    @ui.button(label='ステージ図面', style=discord.ButtonStyle.green)
    async def stage_button(self, interaction: discord.Interaction, button: ui.Button):
        image_1 = discord.File(
            f"./images/stages/{str(self.stage_info['rule']['key']).lower()}/{self.stage_info['stages'][0]['id']}.png",
            filename='image.png', description=f"{self.stage_info['stages'][0]['name']} - Twitter @Sunfish_Drawing")
        image_2 = discord.File(
            f"./images/stages/{str(self.stage_info['rule']['key']).lower()}/{self.stage_info['stages'][1]['id']}.png",
            filename='image.png', description=f"{self.stage_info['stages'][1]['name']} - Twitter @Sunfish_Drawing")

        await interaction.response.send_message('ステージ図面\n図面制作者：Sunfish(まんぼう)様 @Sunfish_Drawing', files=[image_1, image_2], ephemeral=True)


async def setup(bot):
    await bot.add_cog(Splatoon(bot))
