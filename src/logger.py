import sys
import re
from time import sleep


class Logger(object):
    def __init__(self, bar, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w")
        self.antiANSI = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        self.bar = bar
    def start(self):
        sys.stdout = self

    def write(self, message):
        message = self.antiANSI.sub('', message)
        self.log.write(message)

    def print(self, message):
        self.write(message)

    def stop(self):
        sys.stdout = self.terminal

    def bar(self):
        self.stop()
        self.bar()
        self.start()

    def isatty(a):
        pass

    def flush(a):
        pass
