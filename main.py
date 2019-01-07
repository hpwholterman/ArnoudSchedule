


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
        for l in schedule:
            d = '-' if l.upper() not in ['D', 'N'] else l.upper()
            week.append(d)
            if len(week) >= 7:
                self.template.append(week)
                week = list()
        return self.template


p1 = 'DDD--NN--DDD--'
p2 = '--DDD--DDD--NN'

a = ArnSchedule(p1)
print(a.template)