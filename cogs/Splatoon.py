import os
import random
import json
import requests
from typing import Optional

from discord.commands import slash_command, Option
from discord.ext import commands
from discord import Embed, AllowedMentions

from libs import Convert


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
        self.convert = bot.convert

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

        embed = Embed(title=f'Splatoon2 ステージ情報 | {"サーモンラン "if stage_type == "coop" else s_type + "マッチ"}',
                      description=create_text(stage_info, stage_type),
                      color=stage_color[s_type])
        embed.set_image(url=image_url)

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Splatoon(bot))
