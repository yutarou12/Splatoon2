import requests
from typing import Optional, Union


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
