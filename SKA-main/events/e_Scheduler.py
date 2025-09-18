import time

from .event import Event

class Scheduler(Event):
    def __init__(self) -> None:
        self.flag = 0
        self.data = ''
        self.name = "Scheduler"
        self.description = "日程调度"

    def scheduler(self):
        '''
        日程调度,输入日程表可以在适时运行任务

        args:
            待办: 日程表.json

        '''
        # demo: 早八报时
        if time.localtime().tm_hour == 8 and time.localtime().tm_min == 0:
            self.flag = 1
            self.data = "早八报时"  #task
