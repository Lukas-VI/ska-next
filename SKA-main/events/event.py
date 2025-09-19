import asyncio

class Event:
    '''
    所有自定义事件类的基类
    '''
    def __init__(self):
        self.name = "BaseEvent"
        self.flag = 0
        self.data = ''
        self.async_event = None  # 添加asyncio.Event支持
        self.monitoring_task = None  # 监听任务
        # 自动启动监听任务
        self._start_monitoring()

    def set_async_event(self, event):
        '''
        设置asyncio.Event对象，用于异步通知
        '''
        self.async_event = event

    def _start_monitoring(self):
        '''
        启动持续监听任务
        '''
        if self.monitoring_task is None or self.monitoring_task.done():
            self.monitoring_task = asyncio.create_task(self._monitor_loop())

    async def _monitor_loop(self):
        '''
        持续监听循环
        '''
        while True:
            self.slot()
            # 短暂等待以避免过度占用CPU
            await asyncio.sleep(1)

    #使用魔法方法重载实例的值为事件flag方便调用
    def __int__(self):
        self.slot()
        return self.flag
    
    def slot(self):
        '''
        在此写检测事件是否发生的逻辑
        '''
        pass