import os
import random
import json
import requests
import math
import asyncio
from typing import Optional

from discord.commands import slash_command, Option
from discord.ext import commands, pages
import discord

from libs import Convert


def create_text(info, rule):
    if rule == 'coop':
        stage = info["stage"]["name"] if info["stage"] else "未発表"

        s_t = str(info['start']).replace('-', '/', 2).replace('T', ' | ')
        e_t = str(info['end']).replace('-', '/', 2).replace('T', ' | ')
        weapons = ''
        if info['weapons']:
            for we in info['weapons']:
                weapons += f'・{we["name"]}\n'
        else:
            weapons = '未発表'

        de_msg = f'**ステージ**\n```\n{stage}\n```\n**支給ブキ**\n```\n{weapons}```\n' \
                 f'**時間帯**\n```\nSTART: {s_t}\nEND: {e_t}\n```'
    else:
        rule_name = info["rule"]
        stage = f'・{info["maps"][0]}\n・{info["maps"][1]}'
        s_t = str(info['start']).replace('-', '/', 2).replace('T', ' | ')
        e_t = str(info['end']).replace('-', '/', 2).replace('T', ' | ')

        de_msg = f'**ルール**\n```\n{rule_name}```\n**ステージ**\n```\n{stage}\n```\n' \
                 f'**時間帯**\n```\nSTART: {s_t}\nEND: {e_t}\n```'

    return de_msg


def create_text_3(info):
    rule_name = info["rule"]['name']
    stage = f'・{info["stages"][0]["name"]}\n・{info["stages"][1]["name"]}'
    s_t = str(info['start_time']).replace('-', '/', 2).replace('T', ' | ')
    e_t = str(info['end_time']).replace('-', '/', 2).replace('T', ' | ')

    de_msg = f'**ルール**\n```\n{rule_name}```\n**ステージ**\n```\n{stage}\n```\n' \
             f'**時間帯**\n```\nSTART: {s_t.split("+")[0]}\nEND: {e_t.split("+")[0]}\n```'

    return de_msg


class Splatoon(commands.Cog):
    """スプラトゥーンステージ情報のコア"""
    def __init__(self, bot):
        self.bot = bot
        self.s_endpoint = 'https://stat.ink/api/v2'
        self.convert: Convert = bot.convert

    @slash_command(name='stage')
    async def slash_stage(self, ctx,
                          s_type: Option(str, "ステージ情報を選択してください", name='ルール', choices=["レギュラー", "ガチ", "リーグ", "サーモンラン"]),
                          s_next_text: Option(str, "時間帯", name='時間帯', choices=["今", "次"], default='今')):
        """Splatoon2のステージ情報を表示するコマンド"""
        stage_dict = {'レギュラー': 'regular', 'ガチ': 'gachi', 'リーグ': 'league', 'サーモンラン': 'coop'}
        stage_color = {'レギュラー': 261888, 'ガチ': 14840346, 'リーグ': 15409787, 'サーモンラン': 15442812}
        stage_type = stage_dict[s_type]
        stage_time_dict = {'今': False, '次': True}
        stage_time = stage_time_dict[s_next_text]

        stage_info = self.convert.get_stage(stage_type, stage_time)
        if stage_type == 'coop':
            image_url = stage_info['stage']['image']
        else:
            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

        embed = discord.Embed(title=f'Splatoon2 ステージ情報 | {"サーモンラン "if stage_type == "coop" else s_type + "マッチ"}',
                              description=create_text(stage_info, stage_type),
                              color=stage_color[s_type])
        embed.set_image(url=image_url)

        return await ctx.respond(embed=embed)

    @slash_command(name='stage3')
    async def slash_stage3(self, ctx,
                           s_type: Option(str, "ステージ情報を選択してください", name='ルール', choices=["レギュラー", "バンカラ(チャレンジ)", "バンカラ(オープン)"]),
                           s_next_text: Option(str, "時間帯", name='時間帯', choices=["今", "次"], default='今')
                           ):
        """Splatoon3のステージ情報を表示するコマンド"""
        stage_dict = {'レギュラー': 'regular', 'バンカラ(チャレンジ)': 'bankara-challenge', 'バンカラ(オープン)': 'bankara-open'}
        stage_name = {'レギュラー': 'レギュラーマッチ', 'バンカラ(チャレンジ)': 'バンカラマッチ (チャレンジ)', 'バンカラ(オープン)': 'バンカラマッチ (オープン)'}
        stage_color = {'レギュラー': 261888, 'バンカラ(チャレンジ)': 14840346, 'バンカラ(オープン)': 15409787}
        stage_type = stage_dict[s_type]
        stage_time_dict = {'今': False, '次': True}
        stage_time = stage_time_dict[s_next_text]

        stage_info = self.convert.get_stage_3(stage_type, stage_time)
        # image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

        embed = discord.Embed(title=f'Splatoon3 ステージ情報 | {stage_name[s_type]}',
                              description=create_text_3(stage_info),
                              color=stage_color[s_type])
        # embed.set_image(url=image_url)

        return await ctx.respond(embed=embed)

    @slash_command(name='weapon')
    @commands.cooldown(1, 60*60*2, commands.BucketType.user)
    async def slash_weapon(self, ctx):
        """ブキガチャコマンド"""
        weapon = self.convert.get_weapon()
        weapon_list_jp = [(i['name']['ja_JP'], i['splatnet']) for i in weapon]
        weapons = random.sample(weapon_list_jp, 6)
        weapon_files = [discord.File(f'./images/weapons/{f[1]}.png', filename='image.png') for f in weapons]

        embed = discord.Embed(title='ブキガチャ',
                              description='ブキチ君が迷っている...')
        embed.set_image(url='attachment://image.png')

        await ctx.respond(embed=embed, file=weapon_files[0])

        await asyncio.sleep(1)

        for i in range(1, len(weapon_files)):
            await ctx.interaction.edit_original_message(embed=embed, file=weapon_files[i])
            await asyncio.sleep(1)

        ch_weapon_name, ch_weapon_id = random.choice(weapon_list_jp)

        file = discord.File(f'./images/weapons/{ch_weapon_id}.png', filename='image.png')

        embed = discord.Embed(title='ブキガチャ 結果',
                              description=f'{ctx.author.mention}さんが引いたのは...\n**{ch_weapon_name}** だ！\nこの武器で対戦してみよう！')
        embed.set_image(url='attachment://image.png')

        await asyncio.sleep(1.5)
        return await ctx.interaction.edit_original_message(file=file, embed=embed)

    @slash_weapon.error
    async def slash_weapon_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await ctx.respond(f'{math.floor(error.retry_after / 60)} 分後に利用できます。', ephemeral=True)
        else:
            raise error

    @slash_command(name='list')
    async def stage_list(self, ctx):
        """スプラトゥーンステージ情報の一覧を表示するコマンド"""
        await ctx.defer(ephemeral=True)
        stage_color = {'レギュラー': 261888, 'ガチ': 14840346, 'リーグ': 15409787, 'サーモンラン': 15442812}
        r_stage_info = self.convert.get_stage('regular', stage_all=True)
        g_stage_info = self.convert.get_stage('gachi', stage_all=True)
        l_stage_info = self.convert.get_stage('league', stage_all=True)
        c_stage_info = self.convert.get_stage('coop', stage_all=True)

        regular_page = []
        for info in r_stage_info:
            embed = discord.Embed(title=f'Splatoon2 ステージ情報 | レギュラーマッチ',
                                  description=create_text(info, 'regular'),
                                  color=stage_color['レギュラー'])
            embed.set_image(url=random.choice([info['maps_ex'][0]['image'], info['maps_ex'][1]['image']]))
            regular_page.append(embed)

        gachi_page = []
        for info in g_stage_info:
            embed = discord.Embed(title=f'Splatoon2 ステージ情報 | ガチマッチ',
                                  description=create_text(info, 'gachi'),
                                  color=stage_color['ガチ'])
            embed.set_image(url=random.choice([info['maps_ex'][0]['image'], info['maps_ex'][1]['image']]))
            gachi_page.append(embed)

        league_page = []
        for info in l_stage_info:
            embed = discord.Embed(title=f'Splatoon2 ステージ情報 | リーグマッチ',
                                  description=create_text(info, 'league'),
                                  color=stage_color['リーグ'])
            embed.set_image(url=random.choice([info['maps_ex'][0]['image'], info['maps_ex'][1]['image']]))
            league_page.append(embed)

        coop_page = []
        for info in c_stage_info:
            embed = discord.Embed(title=f'Splatoon2 ステージ情報 | サーモンラン',
                                  description=create_text(info, 'coop'),
                                  color=stage_color['サーモンラン'])
            if info['stage']:
                embed.set_image(url=info['stage']['image'])
            coop_page.append(embed)

        page_groups = [
            pages.PageGroup(
                pages=regular_page,
                label="レギュラーマッチ",
                description="レギュラーマッチのステージ情報一覧"
            ),
            pages.PageGroup(
                pages=gachi_page,
                label="ガチマッチ",
                description="ガチマッチのステージ一覧"
            ),
            pages.PageGroup(
                pages=league_page,
                label="リーグマッチ",
                description="リーグマッチのステージ一覧"
            ),
            pages.PageGroup(
                pages=coop_page,
                label="サーモンラン",
                description="サーモンランのステージ一覧"
            ),
        ]

        paginator = pages.Paginator(pages=page_groups, show_menu=True)
        await paginator.respond(ctx.interaction, ephemeral=True)


def setup(bot):
    bot.add_cog(Splatoon(bot))
