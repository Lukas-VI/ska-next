from .event import Event
from server import QQHttpServer

class QQnewMsg(Event):
    def __init__(self, qq_server=None):
        super().__init__()
        self.name = "QQnewMsg"
        self.description = "QQ新消息事件"
        self.flag = 0
        self.data = ''
        if qq_server is not None:
            self.qq_server = qq_server
        else:
            self.qq_server = QQHttpServer()
            print("异常！请检查QQHttpServer是否正常启动")
    def slot(self):
        if self.qq_server.detact_new_msg():
            self.flag = 1
