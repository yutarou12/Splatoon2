import requests
from typing import Optional, Union

from discord import app_commands
from libs.Error import NotOwner


def is_owner():
    async def predicate(interaction) -> bool:
        if not interaction.user.id == 534994298827964416:
            raise NotOwner('You are not Owner')
        return True
    return app_commands.check(predicate)


class Convert:

    def __init__(self):
        pass

    def get_api(self, url: str) -> dict:
        """
        Get the API data.
        :param url: API URL
        :return: dict
        """

        headers = {'User-Agent': 'DiscordBot-Splatoon/1.0 (twitter @yutarou1241477) (Contact yutarou12@syutarou.xyz)'}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()['result']
        else:
            return res.json()

    def get_api_3(self, url: str, result_name='results') -> Optional[dict|None] :
        """
        Get the API data.
        :param url: API URL
        :param result_name: result name
        :return: dict | None
        """

        headers = {'User-Agent': 'DiscordBot-Splatoon/1.0 (twitter @yutarou1241477) (Contact yutarou12@syutarou.xyz)'}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get(result_name)
        else:
            return res.json()

    def get_stage_all(self):
        """
        Get the current all stage of Splatoon3.
        :return: Dict
        """
        data = self.get_api_3('https://spla3.yuu26.com/api/schedule', result_name='result')
        if data is None:
            return None
        regular = data['regular'][1]
        bankara_challenge = data['bankara_challenge'][1] if data.get('bankara_challenge') and len(data.get('bankara_challenge')) >= 2 else None
        bankara_open = data['bankara_open'][1] if data.get('bankara_open') and len(data.get('bankara_open')) >= 2 else None
        try:
            x = data['x'][1] if data.get('x') else None
        except IndexError:
            x = None
        result_data = {'regular': regular, 'bankara_challenge': bankara_challenge, 'bankara_open': bankara_open, 'x': x}
        return result_data

    def get_stage_3(self, game, time_next: bool = False, stage_all: bool = False) -> Union[dict, bool]:
        """
        Get the current stage of Splatoon3.
        :param game: ゲームタイプ
        :param time_next: 時間帯
        :param stage_all: 全ステージ
        :return: Union[dict, bool]
        """

        if game == 'regular':
            if stage_all:
                res = self.get_api_3('https://spla3.yuu26.com/api/regular/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api_3('https://spla3.yuu26.com/api/regular/next')
                    return res[0]
                else:
                    res = self.get_api_3('https://spla3.yuu26.com/api/regular/now')
                    return res[0]

        elif game == 'bankara-challenge':
            if stage_all:
                res = self.get_api_3('https://spla3.yuu26.com/api/bankara-challenge/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api_3('https://spla3.yuu26.com/api/bankara-challenge/next')
                    return res[0]
                else:
                    res = self.get_api_3('https://spla3.yuu26.com/api/bankara-challenge/now')
                    return res[0]

        elif game == 'bankara-open':
            if stage_all:
                res = self.get_api_3('https://spla3.yuu26.com/api/bankara-open/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api_3('https://spla3.yuu26.com/api/bankara-open/next')
                    return res[0]
                else:
                    res = self.get_api_3('https://spla3.yuu26.com/api/bankara-open/now')
                    return res[0]
        elif game == 'coop-grouping':
            if stage_all:
                res = self.get_api_3('https://spla3.yuu26.com/api/coop-grouping/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api_3('https://spla3.yuu26.com/api/coop-grouping/next')
                    return res[0]
                else:
                    res = self.get_api_3('https://spla3.yuu26.com/api/coop-grouping/now')
                    return res[0]
        elif game == 'x':
            if stage_all:
                res = self.get_api_3('https://spla3.yuu26.com/api/x/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api_3('https://spla3.yuu26.com/api/x/next')
                    return res[0]
                else:
                    res = self.get_api_3('https://spla3.yuu26.com/api/x/now')
                    return res[0]
        else:
            return False

    def get_fest_3(self, time_next: bool = False) -> Union[dict, bool]:
        """
        Get the current fest stage of Splatoon3.
        :param time_next: 時間帯
        :return: Union[dict, bool]
        """

        if time_next:
            res = self.get_api_3('https://spla3.yuu26.com/api/fest/next')
            return res[0]
        else:
            res = self.get_api_3('https://spla3.yuu26.com/api/fest/now')
            return res[0]

    def get_stage(self, game, time_next: bool = False, stage_all: bool = False) -> Union[dict, bool]:
        """
        Get the current stage of Splatoon2.
        :param game: ゲームタイプ
        :param time_next: 時間帯
        :param stage_all: 全ステージ
        :return: Union[dict, bool]
        """

        if game == 'regular':
            if stage_all:
                res = self.get_api('https://spla2.yuu26.com/regular/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api('https://spla2.yuu26.com/regular/next')
                    return res[0]
                else:
                    res = self.get_api('https://spla2.yuu26.com/regular/now')
                    return res[0]
        elif game == 'gachi':
            if stage_all:
                res = self.get_api('https://spla2.yuu26.com/gachi/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api('https://spla2.yuu26.com/gachi/next')
                    return res[0]
                else:
                    res = self.get_api('https://spla2.yuu26.com/gachi/now')
                    return res[0]
        elif game == 'league':
            if stage_all:
                res = self.get_api('https://spla2.yuu26.com/league/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api('https://spla2.yuu26.com/league/next')
                    return res[0]
                else:
                    res = self.get_api('https://spla2.yuu26.com/league/now')
                    return res[0]
        elif game == 'coop':
            if stage_all:
                res = self.get_api('https://spla2.yuu26.com/coop/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api('https://spla2.yuu26.com/coop/schedule')
                    return res[1]
                else:
                    res = self.get_api('https://spla2.yuu26.com/coop/schedule')
                    return res[0]
        else:
            return False

    def get_weapon(self, version) -> dict:
        """
        Get the weapon.
        :return: weapon
        """

        res = requests.get(f'https://stat.ink/api/{version}/weapon')
        if res.status_code == 200:
            return res.json()
