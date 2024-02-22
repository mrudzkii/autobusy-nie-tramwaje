import json
import time
from collections import defaultdict
import requests


def download_positions(seconds):
    res = defaultdict(set)
    n = 0
    while n < seconds//10:
        request = requests.get('https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id= '
                               'f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey=7feed0ab-45c9-4c67-ba7a-05ba119f6e99&type=1')
        if (request.text == '    {"result":"B\\u0142\\u0119dna metoda lub parametry wywo\\u0142ania"} \n'
                or request.text == '    {"result":[]} \n'):
            continue
        for d in json.loads(request.text)['result']:
            res[d['VehicleNumber']].add((d['Time'], d['Lat'], d['Lon'], d['Lines'], d['Brigade']))
        time.sleep(10)
        n += 1  # jeśli byl błąd pobrania danych z serwera, to licznik się nie zwiększy.
    return res
