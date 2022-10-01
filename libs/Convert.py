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

    def get_api_3(self, url: str) -> dict:
        """
        Get the API data.
        :param url: API URL
        :return: dict
        """

        headers = {'User-Agent': 'DiscordBot-Splatoon/1.0 (twitter @yutarou1241477) (Contact yutarou12@syutarou.xyz)'}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()['results']
        else:
            return res.json()

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
        elif game == 'coop-grouping-regular':
            if stage_all:
                res = self.get_api_3('https://spla3.yuu26.com/api/coop-grouping-regular/schedule')
                return res
            else:
                if time_next:
                    res = self.get_api_3('https://spla3.yuu26.com/api/coop-grouping-regular/next')
                    return res[0]
                else:
                    res = self.get_api_3('https://spla3.yuu26.com/api/coop-grouping-regular/now')
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

    def get_weapon(self) -> dict:
        """
        Get the weapon.
        :return: weapon
        """

        res = requests.get('https://stat.ink/api/v2/weapon')
        if res.status_code == 200:
            return res.json()
