from discord import app_commands, ui, Embed
from discord.app_commands import Choice
from discord.ext import commands
import discord


class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='auto-setting')
    async def slash_auto_setting(self, interaction):
        """自動送信機能に載る情報を変更できます。"""
        # TODO: サーバーデータを読み込む
        data = {'レギュラー': True, 'バンカラC': True, 'バンカラO': True, 'x': False, 'サーモン': True}

        view = ViewSetting(data=data)

        embed = Embed(title='自動送信機能 設定画面',
                      description='現在の設定です。')
        embed.add_field(name='✅ レギュラーマッチ', value='ㅤ', inline=False)
        embed.add_field(name='✅ バンカラマッチ(チャレンジ)', value='ㅤ', inline=False)
        embed.add_field(name='✅ バンカラマッチ(オープン)', value='ㅤ', inline=False)
        embed.add_field(name='❌ xマッチ', value='ㅤ', inline=False)
        embed.add_field(name='✅ サーモンラン', value='ㅤ', inline=False)
        await interaction.response.send_message(embed=embed, view=view)
        await view.wait()
        # TODO:処理完了のメッセージを設定する
        if view.value is None:
            print('Timed out...')
        elif view.value:
            print('Premium.OK')
        else:
            print('Premium.NO')

class ViewSetting(ui.View):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.value = None


    @ui.button(emoji='<:battle_regular:1021769457221255228>')
    async def regular_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if interaction.message:
            embed = interaction.message.embeds[0]
            embed.remove_field(0)
            hoge = False if self.data['レギュラー'] else True
            embed.insert_field_at(0, name=f'{"✅" if hoge else "❌"} レギュラーマッチ', value='ㅤ', inline=False)
            self.data['レギュラー'] = hoge
            await interaction.edit_original_response(embed=embed)

    @ui.button(emoji='<:battle_gachi:1021769458987057233>')
    async def bankara_1_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if interaction.message:
            embed = interaction.message.embeds[0]
            embed.remove_field(1)
            hoge = False if self.data['バンカラC'] else True
            embed.insert_field_at(1, name=f'{"✅" if hoge else "❌"} バンカラマッチ(チャレンジ)', value='ㅤ', inline=False)
            self.data['バンカラC'] = hoge
            await interaction.edit_original_response(embed=embed)

    @ui.button(emoji='<:battle_gachi:1021769458987057233>')
    async def bankara_2_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if interaction.message:
            embed = interaction.message.embeds[0]
            embed.remove_field(2)
            hoge = False if self.data['バンカラO'] else True
            embed.insert_field_at(2, name=f'{"✅" if hoge else "❌"} バンカラマッチ(オープン)', value='ㅤ', inline=False)
            self.data['バンカラO'] = hoge
            await interaction.edit_original_response(embed=embed)

    @ui.button(emoji='<:battle_x:1053456405455183982>')
    async def x_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if interaction.message:
            embed = interaction.message.embeds[0]
            embed.remove_field(3)
            hoge = False if self.data['x'] else True
            embed.insert_field_at(3, name=f'{"✅" if hoge else "❌"} xマッチ', value='ㅤ', inline=False)
            self.data['x'] = hoge
            await interaction.edit_original_response(embed=embed)

    @ui.button(emoji='<:battle_salmonrun:1021769464221540392>')
    async def coop_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        if interaction.message:
            embed = interaction.message.embeds[0]
            embed.remove_field(4)
            hoge = False if self.data['サーモン'] else True
            embed.insert_field_at(4, name=f'{"✅" if hoge else "❌"} サーモンラン', value='ㅤ', inline=False)
            self.data['サーモン'] = hoge
            await interaction.edit_original_response(embed=embed)

    @ui.button(emoji='<:check_box:1057114619744890961>')
    async def check_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer()
        view = SubmitView(self.data)
        await interaction.followup.send(content='**これで変更を決定しますか？**', view=view)
        await view.wait()
        self.value = view.value
        self.stop()
        await interaction.message.edit(view=None)


class SubmitView(ui.View):
    def __init__(self, data):
        super().__init__()
        self.value = None
        self.data = data

    # TODO: データをデーターベースに書き込む処理を入れる
    @ui.button(label='はい', style=discord.ButtonStyle.blurple)
    async def ok_button(self, interaction: discord.Interaction, button: ui.Button):
        print(self.data)
        await interaction.message.edit(content='保存OK')
        self.value = True
        self.stop()
        await interaction.message.edit(view=None)

    @ui.button(label='いいえ', style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: ui.Button):
        print(self.data)
        await interaction.message.edit(content='保存NO')
        self.value = False
        self.stop()
        await interaction.message.edit(view=None)


async def setup(bot):
    await bot.add_cog(Premium(bot))