import datetime


class CountDown:
    def __init__(self, element, actions, time=3):
        self.element = element
        self.init_time = time
        self.time = time
        self.actions = actions
        self.element.configure(text=f"{self.time}")

    def run(self):
        def count():
            new_time = self.time - 1
            if new_time < 0:
                self.element.after_cancel(self.after)
                for action in self.actions:
                    action()
            else:
                self.time = new_time
                self.element.configure(text=f"{self.time}")
                self.after = self.element.after(1000, count)

        count()

    def start(self):
        self.run()

    def reset(self):
        self.time = self.init_time


class Chronometer:
    def __init__(self, element):
        self.element = element
        self.duration_at_pause = None
        self.duration = None

    def ok_for_bonus(self):
        total_seconds = int(self.duration.total_seconds())
        if total_seconds < 4:
            return True
        return False

    def run(self):
        def count():
            self.duration = datetime.datetime.now() - self.start_time
            if self.duration_at_pause:
                self.duration += self.duration_at_pause
            total_seconds = self.duration.total_seconds()
            self.element.configure(text=f"{total_seconds:.1f} s")
            self.after = self.element.after(100, count)

        count()

    def pause(self):
        if self.duration_at_pause is None:
            self.duration_at_pause = datetime.datetime.now() - self.start_time
        else:
            duration = datetime.datetime.now() - self.start_time
            self.duration_at_pause += duration
        if self.after:
            self.element.after_cancel(self.after)

    def start(self):
        self.start_time = datetime.datetime.now()
        self.run()

    def resume(self):
        self.start()
