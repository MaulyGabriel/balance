import threading


class TimerProcess:

    def __init__(self, limit):
        self.process = None
        self.limit = limit
        self.interruption = False

    def start_process(self, callback, args):
        if self.process is None and self.interruption is False:
            self.process = threading.Timer(self.limit, callback, args)
            self.process.start()
        else:
            self.interruption = False

    def stop_process(self):

        if self.process is not None:
            self.process.cancel()
            self.process = None
            self.interruption = True
