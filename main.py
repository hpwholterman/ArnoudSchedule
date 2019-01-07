from itertools import groupby, filterfalse

from enum import Enum


class DayType(Enum):
    DAY = 1
    NIGHT = 2
    DAY_OR_NIGHT = 3
    FREE = 4


class ArnSchedule(object):
    schedule = None
    template = None

    def __init__(self, schedule):
        self.load_schedule(schedule)

    def load_schedule(self, schedule):
        if len(schedule) != 14:
            raise Exception('Lengte moet 14 zijn. Gevonden lengte: %s' % schedule)
        self.template = list()
        week = list()
        for l in schedule.upper():
            d = DayType.FREE
            if l == 'D':
                d = DayType.DAY
            elif l == 'N':
                d = DayType.NIGHT
            week.append(d)
            if len(week) >= 7:
                self.template.append(week)
                week = list()
        self.schedule = self.template * 4
        return self.schedule

    def sum_schedule(self, day_type=DayType.DAY_OR_NIGHT):
        weeks, days = list(), [0, 0, 0, 0, 0, 0, 0]
        if day_type == DayType.DAY_OR_NIGHT:
            day_filter = lambda x: x in [DayType.DAY, DayType.NIGHT]
        else:
            day_filter = lambda x: x == day_type
        for w in range(8):
            weeks.append(len([i for i in self.schedule[w] if day_filter(i)]))
            for d in range(7):
                if day_filter(self.schedule[w][d]):
                    days[d] += 1
        return weeks, days


p1 = 'DDD--NN--DDD--'
p2 = '--DDD--DDD--NN'

a = ArnSchedule(p1)
for w in a.schedule:
    print(w)

x = a.sum_schedule()
print(x)
