import requests
from typing import Optional, Union


class Convert:

    def __init__(self):
        pass

    def get_stage(self, game, time_next: bool) -> Union[dict, bool]:
        """
        Get the current stage of Splatoon2.
        :param game: ゲームタイプ
        :param time_next: 時間帯
        :return: Union[dict, bool]
        """

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
        else:
            return False
