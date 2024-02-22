import requests
import json
from collections import defaultdict
from datetime import datetime
import pickle


# Get latitude and longitude for every stop in Warsaw
def download_stops_locations():
    url = ('https://api.um.warszawa.pl/api/action/dbstore_get/'
           '?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey=7feed0ab-45c9-4c67-ba7a-05ba119f6e99')
    stops = requests.get(url)
    stops_locations = {}
    for outer in json.loads(stops.text)['result']:
        zespol, slupek, dlg, szer = '', '', '', ''
        for d in outer['values']:
            if d['key'] == 'zespol':
                zespol = d['value']
            elif d['key'] == 'slupek':
                slupek = d['value']
            elif d['key'] == 'szer_geo':
                szer = d['value']
            elif d['key'] == 'dlug_geo':
                dlg = d['value']
        stops_locations[(zespol, slupek)] = (szer, dlg)
    return stops_locations


# For every bus get stop id's on which it stops
def download_timetables():
    stops = defaultdict(set)
    rozklady = requests.get('https://api.um.warszawa.pl/api/action/public_transport_routes/'
                            '?apikey=7feed0ab-45c9-4c67-ba7a-05ba119f6e99')
    for line in json.loads(rozklady.text)['result'].keys():
        stops[line] = set()
        for value in json.loads(rozklady.text)['result'][line].values():
            for stop in value.values():
                stops[line].add((stop['nr_zespolu'], stop['nr_przystanku']))
    return stops


def download_all():
    stops_locations = download_stops_locations()
    stops = download_timetables()

    try:
        with open("lines-where-when-full.pkl", 'rb') as plik:
            lines_where_when = pickle.load(plik)
    except IOError:
        lines_where_when = {}

    n = 0
    for line in stops.keys():
        times = {}
        if line in lines_where_when.keys():
            n += 1
            print(f"skipped line {line} because it's already been processed")
            continue
        for stop in stops[line]:
            url = (f'https://api.um.warszawa.pl/api/action/dbtimetable_get/'
                   f'?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238&busstopId={stop[0]}'
                   f'&busstopNr={stop[1]}&line={line}&apikey=7feed0ab-45c9-4c67-ba7a-05ba119f6e99')
            arrivals = requests.get(url)
            while (arrivals.text == '    ' or
                   arrivals.text == '    {"result":"B\\u0142\\u0119dna metoda lub parametry wywo\\u0142ania"} \n'):
                arrivals = requests.get(url)
            arrivals_for_bus_on_stop = []
            for outer in json.loads(arrivals.text)['result']:
                time = ''
                brigade = ''
                successful = True
                for d in outer['values']:
                    if d['key'] == 'czas':
                        try:
                            time = datetime.strptime(d['value'], '%H:%M:%S')
                        except ValueError:
                            successful = False
                            pass
                    elif d['key'] == 'brygada':
                        brigade = d['value']
                if successful:
                    arrivals_for_bus_on_stop.append((str(time.time()), brigade))
            try:
                times[stops_locations[(stop[0], stop[1])]] = arrivals_for_bus_on_stop
            except KeyError:
                pass
        lines_where_when[line] = times
        n += 1
        print(f"finished processing line {line}, processed {n} lines")
    return lines_where_when
