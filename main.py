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
    _offset = 0

    def __init__(self, name, schedule):
        self.load_schedule(schedule)
        self.name = name
        self._template_string = schedule

    def __str__(self):
        def print_day(dt):
            if dt == DayType.NIGHT:
                return 'N'
            elif dt == DayType.DAY:
                return 'D'
            else:
                return '-'

        day_codes = list()
        for w in self._schedule:
            day_codes += [print_day(d) for d in w]
        return ''.join(day_codes) + ' -> ' + self.name

    def load_schedule(self, schedule):
        if len(schedule) != 28:
            raise Exception('Lengte moet 28 zijn. Gevonden lengte: %s' % len(schedule))
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
        self._schedule = self._template * 2
        self._offset = 0

    def shift_schedule(self, offset):
        if offset <= 0:
            self.reset_schedule()
            return
        self._schedule = [self._template[(i + offset) % 4] for i in range(8)]
        self._offset = offset


class ArnRoster(object):
    schedules = list()

    def __init__(self):
        self.schedules = list()

    def print_schedules(self):
        for s in self.schedules:
            print(s)

    def calc(self, day_type=DayType.DAY_OR_NIGHT):
        ret = sum([s.translate_schedule(day_type) for s in self.schedules])
        return ret


class ArnRosterOptimizer(object):
    _roster = None
    iterate_factor = 10
    day_margin = 1.1
    night_margin = 1.25

    def __init__(self, roster):
        self._roster = roster

    def get_stdevs(self):
        day_sched, night_sched = self._roster.calc(day_type=DayType.DAY), \
                                 self._roster.calc(day_type=DayType.NIGHT)
        day_std, night_std = np.std(day_sched.sum(axis=1)), \
                             np.std(night_sched.sum(axis=1))
        return day_std, night_std

    def optimize(self):
        # start_roster = deepcopy(self._roster)
        day_std, night_std = self.get_stdevs()
        best_day_std, best_night_std = day_std, night_std
        print('->',
              round(best_day_std, 3),
              round(best_night_std, 3)
              )
        prev_it, calc_idx, sched_count = 0, 0, len(self._roster.schedules)
        for it in range(sched_count * self.iterate_factor):
            sch_idx = randrange(sched_count)
            calc_schedule = self._roster.schedules[sch_idx]
            for test_offset in range(1, 4):
                prev_offset = calc_schedule._offset
                calc_schedule.shift_schedule(test_offset)
                day_std, night_std = self.get_stdevs()
                if ((day_std < best_day_std and night_std <= best_night_std * self.night_margin)
                        or (day_std <= best_day_std * self.day_margin and night_std < best_night_std)):
                    best_day_std, best_night_std = day_std, night_std
                    calc_idx, prev_it = sch_idx, it
                    print('%02d' % it,
                          test_offset,
                          round(best_day_std, 3),
                          round(best_night_std, 3),
                          calc_idx
                          )
                else:
                    calc_schedule.shift_schedule(prev_offset)
            if it - prev_it > max(100, sched_count):
                break
        print('Done', it)


def random_schedule():
    return ''.join([choice(['D', '-', 'N', '-']) for i in range(28)])


if __name__ == '__main__':
    rost = ArnRoster()
    for n in range(40):
        rost.schedules.append(ArnSchedule('pers-%s' % n, random_schedule()))

    opt = ArnRosterOptimizer(roster=rost)
    opt.optimize()

