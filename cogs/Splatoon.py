import os
import random
import json
import requests
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
        """スプラトゥーンステージ情報を表示するコマンド"""
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

        await ctx.respond(embed=embed)

    @slash_command(name='list', guild_ids=[881390536504799234])
    async def stage_list(self, ctx):
        """スプラトゥーンステージ情報の一覧を表示するコマンド"""
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
                description="レギュラーマッチのステージ情報一覧",
            ),
            pages.PageGroup(
                pages=gachi_page,
                label="ガチマッチ",
                description="ガチマッチのステージ一覧",
                use_default_buttons=False
            ),
            pages.PageGroup(
                pages=league_page,
                label="リーグマッチ",
                description="リーグマッチのステージ一覧",
            ),
            pages.PageGroup(
                pages=coop_page,
                label="サーモンラン",
                description="サーモンランのステージ一覧",
            ),
        ]

        paginator = pages.Paginator(pages=page_groups, show_menu=True)
        await paginator.respond(ctx.interaction, ephemeral=True)


def setup(bot):
    bot.add_cog(Splatoon(bot))
