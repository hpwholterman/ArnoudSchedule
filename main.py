import csv
import json
from enum import Enum
from random import choice, randrange

import numpy as np


# from copy import deepcopy


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
        self.validate(schedule)
        self.load(schedule)
        self.name = name
        self._template_string = schedule

    def __str__(self):
        return json.dumps(self.json())

    def json(self):
        def get_string(print_func, weeks):
            sched_string = ''
            for w in weeks:
                sched_string += ''.join([print_func(d) for d in w])
            return sched_string

        return dict(name=self.name,
                    template=get_string(self.print_day, self._template),
                    schedule=get_string(self.print_day, self._schedule),
                     )

    @staticmethod
    def print_day(daytype):
        if daytype == DayType.NIGHT:
            return 'N'
        elif daytype == DayType.DAY:
            return 'D'
        else:
            return '-'

    @staticmethod
    def validate(schedule):
        if len(schedule) != 28:
            raise Exception('Lengte moet 28 zijn. Gevonden lengte: %s' % len(schedule))
        if 'ND' in schedule.upper():
            raise Exception('Dagdienst na een nachtdienst gevonden')
        if 'N-D' in schedule.upper():
            raise Exception('N-D gevonden')
        if schedule.count('-') > 14:
            raise Exception('Teveel vrije dagen: %s' % schedule.count('-'))
        return True

    def csv(self):
        def parse_day(self, t):
            day_idx = y % 7
            return dict(naam=self.name,
                        type=t,
                        week=i + 1,
                        day='%s: %s' % (1 + day_idx, days[day_idx]),
                        work=self.print_day(d),
                        )

        days = ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo']
        for i, w in enumerate(self._template):
            for y, d in enumerate(w):
                yield parse_day(self, t='voorkeur')
        for i, w in enumerate(self._schedule):
            for y, d in enumerate(w):
                yield parse_day(self, t='rooster')

    def csv1(self):
        def parse_week(self, t):
            return dict(naam=self.name,
                        type=t,
                        week=i + 1,
                        ma=self.print_day(w[0]),
                        di=self.print_day(w[1]),
                        wo=self.print_day(w[2]),
                        do=self.print_day(w[3]),
                        vr=self.print_day(w[4]),
                        za=self.print_day(w[5]),
                        zo=self.print_day(w[6]),
                        )

        for i, w in enumerate(self._template):
            yield parse_week(self, t='voorkeur')
        for i, w in enumerate(self._schedule):
            yield parse_week(self, t='rooster')

    def load(self, schedule):
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

    def __str__(self):
        return json.dumps(self.json())

    def print_schedules(self):
        for s in self.schedules:
            print(s)

    def calc(self, day_type=DayType.DAY_OR_NIGHT):
        ret = sum([s.translate_schedule(day_type) for s in self.schedules])
        return ret

    def dump_json(self, filename='roster.json'):
        with open(filename, 'w') as f:
            json.dump(obj=[s.json() for s in self.schedules], fp=f)

    def dump_csv1(self, filename='roster1.tsv'):
        with open(filename, 'w') as f:
            fields = ['naam', 'type', 'week', 'ma', 'di', 'wo', 'do', 'vr', 'za', 'zo']
            writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t')
            writer.writeheader()
            for sched in self.schedules:
                for sch_row in sched.csv1():
                    writer.writerow(sch_row)

    def dump_csv(self, filename='roster.tsv'):
        with open(filename, 'w') as f:
            fields = ['naam', 'type', 'week', 'day', 'work']
            writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t')
            writer.writeheader()
            for sched in self.schedules:
                for sch_row in sched.csv():
                    writer.writerow(sch_row)

    def load_json(self, filename):
        err_cnt = 0
        with open(filename, 'r') as f:
            input_dta = json.load(f)
        for inp_sch in input_dta:
            try:
                self.schedules.append(ArnSchedule(inp_sch['name'], inp_sch['template']))
            except Exception as err:
                print('ERROR:', err, '->', inp_sch['name'], inp_sch['template'])
                err_cnt += 1
        return err_cnt == 0


class ArnRosterOptimizer(object):
    _roster = None
    iterate_factor = 10
    iterate_stop = 100
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
            if it - prev_it > max(self.iterate_stop, sched_count):
                print('Done', it)
                break


def random_schedule():
    while True:
        try:
            sched = ''.join([choice(['D', 'D', 'D', '-', 'N', '-']) for i in range(28)])
            ArnSchedule.validate(sched)
            return sched
        except:
            pass


def load_random(roster):
    for n in range(25):
        a_sch = ArnSchedule('pers-%s' % n, random_schedule())
        roster.schedules.append(a_sch)


if __name__ == '__main__':
    rost = ArnRoster()

    # load_random(rost)

    ok = rost.load_json(filename='input.json')
    if not ok:
        exit()

    opt = ArnRosterOptimizer(roster=rost)
    opt.iterate_factor = 25
    opt.iterate_stop = 250
    opt.optimize()

    rost.dump_json()
    rost.dump_csv()
