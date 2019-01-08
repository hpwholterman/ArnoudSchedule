from itertools import groupby, filterfalse

from enum import Enum
from random import choice, randrange
import numpy as np
from copy import deepcopy


class DayType(Enum):
    DAY = 1
    NIGHT = 2
    DAY_OR_NIGHT = 3
    FREE = 4


class ArnSchedule(object):
    _schedule = list()
    _template = list()

    def __init__(self, name, schedule):
        self.load_schedule(schedule)
        self.name = name

    def __str__(self):
        def print_day(dt):
            if dt == DayType.NIGHT:
                return 'N'
            elif dt == DayType.DAY:
                return 'D'
            else:
                return '-'

        return ''.join([print_day(d) for d in self._template[0] + self._template[1]]) + ' -> ' + self.name

    def load_schedule(self, schedule):
        if len(schedule) != 14:
            raise Exception('Lengte moet 14 zijn. Gevonden lengte: %s' % schedule)
        self._template = list()
        week = list()
        for l in schedule.upper():
            d = DayType.FREE
            if l == 'D':
                d = DayType.DAY
            elif l == 'N':
                d = DayType.NIGHT
            week.append(d)
            if len(week) >= 7:
                self._template.append(week)
                week = list()
        self.reset_schedule()
        return self._schedule

    def translate_schedule(self, day_type):
        def workday(x):
            return x in [DayType.DAY, DayType.NIGHT]

        def day_match(x):
            return x == day_type

        day_filter = day_match
        if day_type == DayType.DAY_OR_NIGHT:
            day_filter = workday
        sch = list()
        for w in self._schedule:
            sch.append([int(day_filter(d)) for d in w])
        return np.array(sch)

    def sum_schedule(self, day_type=DayType.DAY_OR_NIGHT):
        x = self.translate_schedule(day_type)
        return dict(week=list(x.sum(axis=1)),
                    weekday=list(x.sum(axis=0))
                    )

    def reset_schedule(self):
        self._schedule = self._template * 4

    def shift_schedule(self):
        self._schedule = self._template[::-1] * 4


class ArnOrganizer(object):
    schedules = list()

    def __init__(self):
        self.schedules = list()

    def print_schedules(self):
        for s in self.schedules:
            print(s)

    def calc(self):
        ret = sum([s.translate_schedule(DayType.DAY_OR_NIGHT) for s in self.schedules])
        return ret


def random_schedule():
    return ''.join([choice(['D', 'D', 'D', 'N', '-', '-', '-']) for i in range(14)])


org = ArnOrganizer()
org.schedules.append(ArnSchedule('edwin', 'DDD--NN--DDD--'))
org.schedules.append(ArnSchedule('piet', '--DDD--DDD--NN'))
for n in range(30):
    org.schedules.append(ArnSchedule('pers-%s' % n, random_schedule()))

print(len(org.schedules))
s = org.calc()
best = (deepcopy(org), np.std(s.sum(axis=1)), np.std(s))
print('->', best[1:])
for r in range(len(org.schedules) * 5):
    i = randrange(len(org.schedules))
    org.schedules[i].shift_schedule()
    s = org.calc()
    s_sd, a_sd = np.std(s.sum(axis=1)), np.std(s)
    if s_sd < best[1]:
        best = (deepcopy(org), np.std(s.sum(axis=1)), np.std(s))
    elif s_sd == best[1] and a_sd < best[2]:
        best = (deepcopy(org), np.std(s.sum(axis=1)), np.std(s))
    else:
        org.schedules[i].reset_schedule()
        continue
    print('%02d' % r, best[1:], i)



