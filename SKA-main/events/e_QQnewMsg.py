from .event import Event
from server import QQHttpServer

class QQnewMsg(Event):
    def __init__(self, qq_server=None, async_event=None):
        # 先调用父类初始化
        super().__init__()
        self.name = "QQnewMsg"
        self.description = "QQ新消息事件"
        self.flag = 0
        self.data = ''
        self.last_data = None  # 保存上一次的数据用于比较
        
        if qq_server is not None:
            self.qq_server = qq_server
        else:
            self.qq_server = QQHttpServer()
            print("异常！请检查QQHttpServer是否正常启动")
            
        # 设置asyncio.Event对象（如果提供）
        if async_event is not None:
            self.set_async_event(async_event)
    
    def slot(self):
        # 直接检查QQ服务器是否有新消息，而不是依赖buffer机制
        try:
            current_data = self.qq_server.recive_data
            if current_data is not None and current_data != self.last_data:
                self.last_data = current_data
                self.flag = 1
                # 如果设置了asyncio.Event，则触发它
                if self.async_event is not None:
                    self.async_event.set()
            else:
                self.flag = 0
        except Exception as e:
            print(f"检查消息时出错: {str(e)}")
            self.flag = 0