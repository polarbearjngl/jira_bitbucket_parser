class WorklogBy(object):

    def __init__(self):
        self.timespent_sec = 0
        self.timespent_min = None
        self.timespent_hours = None

    def update_timespent(self, seconds):
        """Обновить информацию о времени, которое залогано автором.

        Args:
            seconds: Количество секунд, которое будет добавлено.
        """
        self.timespent_sec += seconds
        self.timespent_hours = self.sec_to_hours_mins(s=self.timespent_sec)
        self.timespent_min = self.sec_to_mins(s=self.timespent_sec)

    @staticmethod
    def sec_to_hours_mins(s):
        hours = int(s // 3600)
        mins = (s % 3600) // 60
        if mins == 0:
            return hours
        else:
            mins = str(mins / 60)[2:]
            return float("{}.{}".format(hours, mins))

    @staticmethod
    def sec_to_mins(s):
        return int(str(s // 60))
