from datetime import datetime
from .analyze_speed import fix
from .analyze_speed import distance


def lates(data, lines_where_when, begin, end):
    eps = 0.01  # km
    spoznien_num = 0
    srednia = 0
    lacznie = 0
    maksymalne = 0
    przedzialy_spoznien = {
        '[60s, 2m)': 0,
        '[2m, 5m)': 0,
        '[5m, 10m)': 0,
        '≥10m': 0,
    }
    # begin = '2024-02-21 20:00:00'
    # end = '2024-02-21 22:00:00'
    begin_hour = datetime.strptime(begin, '%Y-%m-%d %H:%M:%S').time()
    end_hour = datetime.strptime(end, '%Y-%m-%d %H:%M:%S').time()
    begin_today = datetime.combine(datetime.date(datetime.today()), begin_hour)
    end_today = datetime.combine(datetime.date(datetime.today()), end_hour)

    for autobus in data.keys():
        # autobus = '7720'  # numer, nie linia
        times_list = fix(list(data[autobus]))
        actual_vs_planned_arrivals = {}
        for marks in times_list:
            line = marks[3]
            brigade = marks[4]
            time = marks[0]
            lat = marks[1]
            lon = marks[2]
            try:
                where_when = lines_where_when[line]
            except KeyError:
                continue
            for where in where_when.keys():
                if distance(lat, lon, float(where[0]), float(where[1])) < eps:
                    for when in where_when[where]:
                        if when[1] == brigade and not (where[0], where[1]) in actual_vs_planned_arrivals.keys():
                            if time < begin or time > end:
                                continue
                            actual_vs_planned_arrivals[(where[0], where[1])] = (time, when)
                            h1 = datetime.strptime(time, '%Y-%m-%d %H:%M:%S').time()
                            d1 = datetime.combine(datetime.date(datetime.today()), h1)
                            h2 = datetime.strptime(when[0], '%H:%M:%S').time()
                            d2 = datetime.combine(datetime.date(datetime.today()), h2)
                            if d2 < begin_today or d2 > end_today:
                                continue
                            delta = d1 - d2
                            lacznie += 1
                            if delta.total_seconds() >= 60:
                                srednia = (spoznien_num * srednia + delta.total_seconds()) / (spoznien_num + 1)
                                spoznien_num += 1
                                maksymalne = max(maksymalne, delta.total_seconds())
                                if delta.total_seconds() >= 600:
                                    przedzialy_spoznien['≥10m'] += 1
                                elif delta.total_seconds() >= 300:
                                    przedzialy_spoznien['[5m, 10m)'] += 1
                                elif delta.total_seconds() >= 120:
                                    przedzialy_spoznien['[2m, 5m)'] += 1
                                else:
                                    przedzialy_spoznien['[60s, 2m)'] += 1
    for przedzial in przedzialy_spoznien.keys():
        wart = przedzialy_spoznien[przedzial]
        przedzialy_spoznien[przedzial] = round(100 * wart / spoznien_num, 2)
    print(f"spoznien: {spoznien_num} ({round((spoznien_num / lacznie) * 100, 2)}%)")
    return przedzialy_spoznien
