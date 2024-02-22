from math import cos, asin, sqrt, pi
from datetime import datetime


def distance(lat1, lon1, lat2, lon2):
    r = 6371  # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))


# Correct data to delete same locations from different times (location in the next request might have not updated)
def fix(data_list):
    res = []
    data_list.sort()
    prev_lat = data_list[0][1]
    prev_lon = data_list[0][2]
    res.append(data_list[0])
    for i in range(1, len(data_list)):
        cur_lat = data_list[i][1]
        cur_lon = data_list[i][2]
        if distance(prev_lat, prev_lon, cur_lat, cur_lon) == 0:
            continue
        res.append(data_list[i])
        prev_lon = cur_lon
        prev_lat = cur_lat
    return res


def count_speeding(data):
    how_many_speeded = 0
    max_overall = 0
    ge_100 = 0
    intervals = {
        4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0
    }
    speeding_places = []
    for key in data.keys():
        times_list = fix(list(data[key]))
        max_speed = 0
        speeding = False
        local = {
            4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0
        }
        for i in range(len(times_list) - 1):
            date1 = datetime.strptime(times_list[i][0], '%Y-%m-%d %H:%M:%S')
            date2 = datetime.strptime(times_list[i+1][0], '%Y-%m-%d %H:%M:%S')
            delta = date2 - date1
            sec = delta.total_seconds()
            if sec == 0:
                continue
            lat1, lon1 = times_list[i][1], times_list[i][2]
            lat2, lon2 = times_list[i+1][1], times_list[i+1][2]
            # get rid of weird data (from places far away from warsaw)
            if lat1 > 90 or lat1 < 0 or lon1 > 90 or lon1 < 0 or lat2 > 90 or lat2 < 0 or lon2 > 90 or lon2 < 0:
                continue
            dis = distance(lat1, lon1, lat2, lon2)
            speed = 3600*dis/sec  # 'dis' is in km, sec is in seconds, and I want to have speed in km/h
            max_speed = max(max_speed, speed)
            if 50 < speed < 100:
                speeding = True
                speeding_places.append((lat2, lon2, speed))
                if speed < 55:
                    if local[4] == 0:
                        local[4] = 1
                        intervals[4] += 1
                elif local[speed//10] == 0:
                    local[speed//10] = 1
                    intervals[speed//10] += 1
            if speed >= 100:
                ge_100 += 1
        if speeding:
            how_many_speeded += 1
        max_overall = max(max_overall, max_speed)
    print(f"speeded {how_many_speeded} out of {len(data.keys())}")
    print(f"speed was greate (or equal) to 100 in {ge_100} cases")
    return intervals, speeding_places


def most_common_speeding_places(speeding_places):
    speeding_rounded = []
    how_many_where = {}
    speeding_places.sort()
    for places in speeding_places:
        speeding_rounded.append((round(places[0], 3), round(places[1], 3), places[2]))
        key = str(round(places[0], 3)) + 'N, ' + str(round(places[1], 3)) + 'E'
        if key in how_many_where.keys():
            tup = how_many_where[key]
            # tup[0] - current number off speeding in a place, tup[1] - average speed
            how_many_where[key] = (tup[0] + 1, (tup[0]*tup[1] + places[2])/(tup[0] + 1))
        else:
            how_many_where[key] = (1, places[2])
    return how_many_where


def speeding_places_dict(how_many_where, count_min, speed_min):
    output = {}
    for where in how_many_where.keys():
        if how_many_where[where][0] > count_min and how_many_where[where][1] > speed_min:
            output[where] = how_many_where[where]
    return output
