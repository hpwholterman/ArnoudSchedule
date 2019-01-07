from itertools import groupby, filterfalse

from enum import Enum


class DayType(Enum):
    DAY = 1
    NIGHT = 2
    DAY_OR_NIGHT = 3
    FREE = 4


class ArnSchedule(object):
    _schedule = list()
    _template = list()

    def __init__(self, schedule):
        self.load_schedule(schedule)

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

    def sum_schedule(self, day_type=DayType.DAY_OR_NIGHT):
        def workday(x):
            return x in [DayType.DAY, DayType.NIGHT]

        def day_match(x):
            return x == day_type

        weeks, days = list(), [0, 0, 0, 0, 0, 0, 0]
        day_filter = day_match
        if day_type == DayType.DAY_OR_NIGHT:
            day_filter = workday
        for w in range(8):
            weeks.append(len([i for i in self._schedule[w] if day_filter(i)]))
            for d in range(7):
                if day_filter(self._schedule[w][d]):
                    days[d] += 1
        return dict(week=weeks, weekday=days)

    def reset_schedule(self):
        self._schedule = self._template * 4

    def shift_schedule(self):
        self._schedule = self._template[::-1] * 4


class ArnOrganizer(object):
    schedules = list()

    def __init__(self):
        self.schedules = list()



p1 = 'DDD--NN--DDD--'
s1 = ArnSchedule(p1)

p2 = '--DDD--DDD--NN'
s2 = ArnSchedule(p2)
print(s2.sum_schedule())
s2.shift_schedule()
print(s2.sum_schedule())
