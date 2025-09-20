import time
import asyncio

from .event import Event

class Scheduler(Event):
    def __init__(self, async_event=None) -> None:
        # 先调用父类初始化
        super().__init__()
        
        self.flag = 0
        self.data = ''
        self.name = "Scheduler"
        self.description = "日程调度"
        
        # 设置asyncio.Event对象（如果提供）
        if async_event is not None:
            self.set_async_event(async_event)
        
        # 自动启动监听任务
        self._start_monitoring()

    def slot(self):
        '''
        日程调度,输入日程表可以在适时运行任务

        args:
            待办: 日程表.json

        '''
        # demo: 早八报时
        if time.localtime().tm_hour == 8 and time.localtime().tm_min == 0:
            self.flag = 1
            self.data = "早八报时"  #task
            # 如果设置了asyncio.Event，则触发它
            if self.async_event is not None:
                self.async_event.set()
        else:
            self.flag = 0

    async def _monitor_loop(self):
        '''
        持续监听循环
        '''
        while True:
            self.slot()
            # 每分钟检查一次调度事件
            await asyncio.sleep(60)