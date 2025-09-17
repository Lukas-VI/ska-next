import time

class IOPack():
    '''
    与SKA交互的标准数据包的基类
    '''
    def __init__(self, pack) -> None:
        self.time = time.time
        self.pack = pack
        self.type = ''
        self.user = ''
        self.content = ''

    def __del__(self):
        print("Class instance destroyed")

    def normlize(self):
        '''
        解析数据包并标准化数据结构
        '''
        self.pack 


class CoreInput(IOPack):
    '''
    作为SKA的输入数据包
    
    数据可以来自: QQ消息, 心跳唤醒, 服务事件等
    '''

    def __init__(self, pack) -> None:
        ''''''
        self.source = ''

    def normlize(self):
        '''
        解析数据包并标准化Input类结构
        '''
        self.pack
        
class CoreOutput(IOPack):
    '''
    基本的输出数据包,记录了SKA / 程序逻辑选择的操作与目标
    '''
    def __init__(self, pack) -> None:
        self.target = ''

    def normlize(self):
        '''
        解析数据包并标准化Input类结构
        '''
        self.pack

class ExpandOutput(CoreOutput):
    '''
    扩增的输出操作,在需要调用工具等时使用
    '''

