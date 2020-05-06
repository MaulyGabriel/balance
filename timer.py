import threading


class TimerProcess:

    def __init__(self):
        self.process = None
        self.limit = 0
        self.interruption = True

    def start_process(self, callback, args):
        if self.process is None:
            self.process = threading.Timer(self.limit, callback, args)
            self.process.start()
            self.interruption = True

    def stop_process(self):
        if self.process is not None:
            self.process.cancel()
            self.process = None
            self.interruption = False

    def restart(self):
        self.interruption = True
