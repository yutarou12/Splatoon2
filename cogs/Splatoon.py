import os
import random
import json
import requests
from typing import Optional

from discord.commands import slash_command, Option
from discord.ext import commands
from discord import Embed, AllowedMentions


def get_stage(game, time_next: bool):
    if game == 'regular':
        if time_next:
            res = requests.get('https://spla2.yuu26.com/regular/next')
            return res.json()['result'][0]
        else:
            res = requests.get('https://spla2.yuu26.com/regular/now')
            return res.json()['result'][0]
    elif game == 'gachi':
        if time_next:
            res = requests.get('https://spla2.yuu26.com/gachi/next')
            return res.json()['result'][0]
        else:
            res = requests.get('https://spla2.yuu26.com/gachi/now')
            return res.json()['result'][0]
    elif game == 'league':
        if time_next:
            res = requests.get('https://spla2.yuu26.com/league/next')
            return res.json()['result'][0]
        else:
            res = requests.get('https://spla2.yuu26.com/league/now')
            return res.json()['result'][0]
    elif game == 'coop':
        if time_next:
            res = requests.get('https://spla2.yuu26.com/coop/schedule')
            return res.json()['result'][1]
        else:
            res = requests.get('https://spla2.yuu26.com/coop/schedule')
            return res.json()['result'][0]


def create_text(info, rule):
    if rule == 'coop':
        stage = info["stage"]["name"]

        s_t = str(info['start']).replace('-', '/', 2).replace('T', ' | ')
        e_t = str(info['end']).replace('-', '/', 2).replace('T', ' | ')
        weapons = ''
        for we in info['weapons']:
            weapons += f'・{we["name"]}\n'

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
        self.spla_api_key = os.getenv('SPLATOON2_KEY')

    @slash_command(name='stage')
    async def slash_stage(self, ctx, s_type: Option(str, "ステージ情報を選択してください", name='ルール', choices=["レギュラー", "ガチ", "リーグ", "サーモンラン"]),
                          s_next_text: Option(str, "時間帯", name='時間帯', choices=["今", "次"], default='今')):
        """スプラトゥーンステージ情報を表示するコマンド"""
        stage_dict = {'レギュラー': 'regular', 'ガチ': 'gachi', 'リーグ': 'league', 'サーモンラン': 'coop'}
        stage_color = {'レギュラー': 261888, 'ガチ': 14840346, 'リーグ': 15409787, 'サーモンラン': 15442812}
        stage_type = stage_dict[s_type]
        stage_time_dict = {'今': False, '次': True}
        stage_time = stage_time_dict[s_next_text]

        stage_info = get_stage(stage_type, stage_time)
        if stage_type == 'coop':
            image_url = stage_info['stage']['image']
        else:
            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

        embed = Embed(title=f'Splatoon2 ステージ情報 | {"サーモンラン "if stage_type == "coop" else s_type + "マッチ"}',
                      description=create_text(stage_info, stage_type),
                      color=stage_color[s_type])
        embed.set_image(url=image_url)

        await ctx.respond(embed=embed)

    @commands.command(description='Splatoon2のステージ情報を取得します',
                      usage='[対戦ルールタイプ] <n(次の時間帯)>')
    async def stage(self, ctx, s_type=None, s_next_text=None):

        if s_next_text == 'n':
            s_next = True
        else:
            s_next = False

        if s_type is None:
            no_type_msg = Embed(description='ステージ情報のタイプ(r, g, l, s)を指定してください\n'
                                            '```r: レギュラーマッチ\ng: ガチマッチ\nl: リーグマッチ\ns: サーモンラン```')
            await ctx.reply(embed=no_type_msg, allowed_mentions=AllowedMentions.none())

        elif s_type == 'r':
            stage_info = get_stage('regular', s_next)
            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

            embed = Embed(title='Splatoon2 ステージ情報 | レギュラーマッチ',
                          description=create_text(stage_info, 'regular'),
                          color=261888)  # カラー:ライトグリーン
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

        elif s_type == 'g':
            stage_info = get_stage('gachi', s_next)

            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

            embed = Embed(title='Splatoon2 ステージ情報 | ガチマッチ',
                          description=create_text(stage_info, 'gachi'),
                          color=14840346)  # カラー:オレンジ
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

        elif s_type == 'l':
            stage_info = get_stage('league', s_next)

            image_url = random.choice([stage_info['maps_ex'][0]['image'], stage_info['maps_ex'][1]['image']])

            embed = Embed(title='Splatoon2 ステージ情報 | リーグマッチ',
                          description=create_text(stage_info, 'league'),
                          color=15409787)  # カラー:ピンク
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())

        elif s_type == 's':
            stage_info = get_stage('coop', s_next)

            image_url = stage_info['stage']['image']
            embed = Embed(title='Splatoon2 ステージ情報 | サーモンラン',
                          description=create_text(stage_info, 'coop'),
                          color=15442812)  # カラー:薄橙
            embed.set_image(url=image_url)
            await ctx.reply(embed=embed, allowed_mentions=AllowedMentions.none())


def setup(bot):
    bot.add_cog(Splatoon(bot))
