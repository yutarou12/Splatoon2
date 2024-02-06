from discord import app_commands, ui, Embed
from discord.ext import commands
import discord


class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name='auto-setting')
    async def slash_auto_setting(self, interaction: discord.Interaction):
        """自動送信機能に載る情報を変更できます。"""
        data = await self.db.premium_data_get(interaction.guild_id, interaction.channel_id)
        f_view = ui.View()
        select = FirstDrop(self.db)
        data_len = 2 - len(data)
        if not data_len:
            for d in data:
                ch = interaction.guild.get_channel(d.get("channel_id"))
                if ch:
                    select.add_option(label=f'{ch.name}', value=d.get("channel_id"))
                else:
                    await self.db.del_premium_data(d.get("channel_id"))
                    select.add_option(label='チャンネル未設定', value='None')
        elif data_len == 2:
            select.add_option(label='チャンネル未設定', value='None')
        else:
            for d in data:
                ch = interaction.guild.get_channel(d.get("channel_id"))
                if ch:
                    select.add_option(label=f'{ch.name}', value=d.get("channel_id"))
                else:
                    await self.db.del_premium_data(d.get("channel_id"))
                    select.add_option(label='チャンネル未設定', value='None')
            for _ in range(data_len):
                select.add_option(label='チャンネル未設定', value='None')

        f_view.add_item(select)

        embed = Embed(title='自動送信機能 設定画面', description='チャンネルを指定してください。')
        await interaction.response.send_message(embed=embed, view=f_view)


class ViewSetting(ui.View):
    def __init__(self, db, data, ch):
        super().__init__()
        self.db = db
        self.data = data
        self.value = None
        self.ch = ch

    @ui.button(emoji='<:check_box:1057114619744890961>', row=2)
    async def check_button(self, interaction: discord.Interaction, button: ui.Button):
        view = SubmitView(db=self.db, data=self.data, ch=self.ch)
        await interaction.response.edit_message(content='**これで変更を決定しますか？**', view=view)
        await view.wait()
        self.value = view.value
        self.stop()
        await interaction.message.edit(view=None)


class CheckButton(ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def callback(self, interaction: discord.Interaction):
        if self.custom_id == 'check':
            return
        else:
            raw_data = self.view.data
            fields_data = ['レギュラー', 'バンカラC', 'バンカラO', 'x', 'サーモン']
            data_convert = {"レギュラー": "レギュラーマッチ", "バンカラC": "バンカラマッチ(チャレンジ)",
                            "バンカラO": "バンカラマッチ(オープン)", "x": "Xマッチ", "サーモン": "サーモンラン"}
            remove_field = fields_data.index(self.custom_id)
            embed = interaction.message.embeds[0]
            embed.remove_field(remove_field)
            hoge = 0 if raw_data.get(f'{self.custom_id}') else 1
            embed.insert_field_at(remove_field,
                                  name=f'{"✅" if hoge else "❌"} {data_convert.get(self.custom_id)}',
                                  value='ㅤ', inline=False)
            raw_data[f'{self.custom_id}'] = hoge
            self.view.data = raw_data
            await interaction.response.edit_message(embed=embed)


class SubmitView(ui.View):
    def __init__(self, db, data, ch):
        super().__init__()
        self.db = db
        self.value = None
        self.data = data
        self.ch = ch

    @ui.button(label='はい', style=discord.ButtonStyle.blurple)
    async def ok_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.db.premium_data_add(interaction.guild_id, self.ch, self.data)
        await interaction.response.edit_message(content='**以下の内容で変更しました**')
        self.value = True
        self.stop()
        await interaction.message.edit(view=None)

    @ui.button(label='いいえ', style=discord.ButtonStyle.danger)
    async def no_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(content='キャンセルしました')
        self.value = False
        self.stop()
        await interaction.message.edit(view=None)


class FirstDrop(ui.Select):
    def __init__(self, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = db
        self.placeholder = 'チャンネルを選択してください'

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'None':
            embed = discord.Embed(description='自動送信するチャンネルを `/auto-set` で設定してくだだい。')
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            data = await self.db.get_premium_data(int(self.values[0]))
            view = ViewSetting(db=self.db, data=data, ch=int(self.values[0]))
            view.add_item(CheckButton(emoji='<:battle_regular:1021769457221255228>', custom_id='レギュラー'))
            view.add_item(CheckButton(emoji='<:battle_gachi:1021769458987057233>', custom_id='バンカラC'))
            view.add_item(CheckButton(emoji='<:battle_gachi:1021769458987057233>', custom_id='バンカラO'))
            view.add_item(CheckButton(emoji='<:battle_x:1053456405455183982>', custom_id='x'))
            view.add_item(CheckButton(emoji='<:battle_salmonrun:1021769464221540392', custom_id='サーモン'))

            embed = Embed(title='自動送信機能 設定画面', description='現在の設定です。')
            embed.add_field(name=f'{"✅" if data.get("レギュラー") else "❌"} レギュラーマッチ', value='ㅤ', inline=False)
            embed.add_field(name=f'{"✅" if data.get("バンカラC") else "❌"} バンカラマッチ(チャレンジ)', value='ㅤ', inline=False)
            embed.add_field(name=f'{"✅" if data.get("バンカラO") else "❌"} バンカラマッチ(オープン)', value='ㅤ', inline=False)
            embed.add_field(name=f'{"✅" if data.get("x") else "❌"} Xマッチ', value='ㅤ', inline=False)
            embed.add_field(name=f'{"✅" if data.get("サーモン") else "❌"} サーモンラン', value='ㅤ', inline=False)
            await interaction.response.edit_message(embed=embed, view=view)
            await view.wait()
            if view.value is None:
                view.stop()


async def setup(bot):
    await bot.add_cog(Premium(bot))
